from tkinter import *
from matplotlib.figure import Figure
import matplotlib
from matplotlib.backends.backend_tkagg import (FigureCanvasTkAgg, NavigationToolbar2Tk)
import numpy as np
import matplotlib.pyplot as plt
from matplotlib.patches import Circle, Polygon
from matplotlib.collections import PatchCollection
import json
from shapely.geometry import Polygon as S_Polygon
from shapely.geometry import LineString
import glob


def text_to_points(txt):
    points = txt.split(',')
    for i, point in enumerate(points):
        new_point = point.replace('(', '')
        new_point = new_point.replace(')', '')
        new_point = new_point.replace(' ', '')
        points[i] = new_point
    final_points = []
    for i in range(0, len(points), 2):
        final_points.append((float(points[i]), float(points[i + 1])))
    return final_points


def list_to_tuple(lst):
    '''
    converts list of length 2 to tuple of floats
    '''
    return float(lst[0]), float(lst[1])


def total_length(points):
    '''
    calculates the length of a valid path
    '''
    total_sum = 0
    for i in range(len(points) - 1):
        point = points[i]
        next_point = points[i + 1]
        total_sum += np.sqrt((next_point[0] - point[0]) ** 2 + (next_point[1] - point[1]) ** 2)
    return total_sum


def draw_settings(ax, settings):
    '''
    draws all the shapes
    '''
    plt.xlim(settings["x_low"], settings["x_high"])
    plt.ylim(settings["y_low"], settings["y_high"])
    poly_patches = []
    for polygon in settings["polygons"]:
        poly_patches.append(Polygon(polygon, color="red"))
    p = PatchCollection(poly_patches, alpha=0.8, facecolors='red')
    ax.add_collection(p)
    circle_patches = []
    for circle in settings["circles"]:
        circle_patches.append(Circle(circle[0], circle[1], color="red"))
    p = PatchCollection(circle_patches, alpha=0.8, facecolors='purple')
    ax.add_collection(p)
    ax.plot(settings["source"][0], settings["source"][1], 'ro', color="black")
    ax.plot(settings["target"][0], settings["target"][1], 'ro', color="black")


def plot(scenario_path, window, inputtxt, label):
    '''
    the function we call after pushing the button and submiting the answer
    '''
    for widget in window.winfo_children():
        if isinstance(widget, matplotlib.backends._backend_tk.NavigationToolbar2Tk):
            widget.destroy()
    fig = plt.figure()
    fig.canvas.manager.toolbar.toolitems = 'None'
    inp = inputtxt.get(1.0, "end")
    fig = Figure(figsize=(4.3, 4.3), dpi=100)
    ax = fig.add_subplot(111)
    with open(scenario_path) as file:
        scenario = json.load(file)
    source = scenario["source"]
    target = scenario["target"]
    polygons = scenario["polygons"]
    circles = scenario["circles"]

    source = list_to_tuple(source)
    target = list_to_tuple(target)
    for i, polygon in enumerate(polygons):
        tuple_polygon = []
        for lst_point in polygon:
            tuple_polygon.append((list_to_tuple(lst_point)))
        polygons[i] = tuple_polygon
    for i, circle in enumerate(circles):
        tuple_circle = [list_to_tuple(circle[0])]
        tuple_circle.append(circle[1])
        circles[i] = tuple_circle

    x_s_list = []
    x_s_list.append(source[0])
    x_s_list.append(target[0])
    for polygon in polygons:
        for point in polygon:
            x_s_list.append(point[0])
    for circle in circles:
        x_s_list.append(circle[0][0] + circle[1])
        x_s_list.append(circle[0][0] - circle[1])

    y_s_list = []
    y_s_list.append(source[1])
    y_s_list.append(target[1])
    for polygon in polygons:
        for point in polygon:
            y_s_list.append(point[1])
    for circle in circles:
        y_s_list.append(circle[0][1] + circle[1])
        y_s_list.append(circle[0][1] - circle[1])

    x_min = min(x_s_list)
    x_max = max(x_s_list)
    y_min = min(y_s_list)
    y_max = max(y_s_list)
    dx = (x_max - x_min) * 0.2
    dy = (y_max - y_min) * 0.2
    settings = {"source": source, "target": target, "polygons": polygons, "circles": circles, "x_low": x_min - dx,
                "x_high": x_max + dx, "y_low": y_min - dy, "y_high": y_max + dy}
    draw_settings(ax, settings)
    if ord(inp[0]) != 10:
        if inp.replace('\n', '') == "None":
            points = [source, target]
        else:
            points = [source] + text_to_points(inp) + [target]
        if valid_path(points, settings):
            label.config(text=f'Valid path! total length is {total_length(points)}', fg='black')
            for i in range(len(points) - 1):
                point = points[i]
                next_point = points[i + 1]
                ax.plot([point[0], next_point[0]], [point[1], next_point[1]], color='black')
        else:
            label.config(text='Invalid path!', fg='red')
    canvas = FigureCanvasTkAgg(fig, master=window)
    canvas.draw()
    canvas.get_tk_widget().pack()
    toolbar = NavigationToolbar2Tk(canvas, window)
    toolbar.update()
    canvas.get_tk_widget().place(x=35, y=0)
    ax.plot()


def valid_line_polygon(start, end, polygon):
    '''
    checks if line passes through a polygon
    '''
    polygon = [(float(tup[0]), float(tup[1])) for tup in polygon]
    s_poly = S_Polygon(polygon)
    s_line = LineString([start, end])
    intersection_line = list(s_poly.intersection(s_line).coords)
    if len(intersection_line) <= 1:
        return True
    for point in intersection_line:
        if point not in polygon:
            return False
    return True


def valid_line_circle(start, end, center, r):
    '''
    checks if line passes through a circle
    '''
    x1, y1 = start
    x2, y2 = end
    xc, yc = center
    x_i = min(x1, x2)
    x_f = max(x1, x2)
    if x2 != x1:
        m = (y2 - y1) / (x2 - x1)
        n = y1 - m * x1
        a = m ** 2 + 1
        b = 2 * (m * (n - yc) - xc)
        c = xc ** 2 + (n - yc) ** 2 - r ** 2
        if b ** 2 - 4 * a * c <= 0:
            return True
        delta = np.sqrt(b ** 2 - 4 * a * c)
        sol1 = (-b + delta) / (2 * a)
        sol2 = (-b - delta) / (2 * a)
        if x_i <= sol1 <= x_f or x_i <= sol2 <= x_f:
            return False
        return True
    if abs(x1 - xc) >= r:
        return True
    y_i = min(y1, y2)
    y_f = max(y1, y2)
    delta = np.sqrt(r ** 2 - (x1 - xc) ** 2)
    sol1 = yc + delta
    sol2 = yc = delta
    if y_i <= sol1 <= y_f or y_i <= sol2 <= y_f:
        return False
    return True


def valid_line_total(start, end, settings):
    '''
    checks if line passes through any polygon or circle
    '''
    for polygon in settings["polygons"]:
        if not valid_line_polygon(start, end, polygon):
            # print(start, end, polygon)
            return False
    for circle in settings["circles"]:
        if not valid_line_circle(start, end, circle[0], circle[1]):
            # print(start, end, circle)
            return False
    return True


def valid_path(points, settings):
    '''
    checks if any line in a path passes through any polygon or circle
    '''
    for i in range(len(points) - 1):
        point = points[i]
        next_point = points[i + 1]
        if not valid_line_total(point, next_point, settings):
            return False
    return True


# run the gui


def GUI(scenario_path=''):
    '''
    the main function
    '''
    window = Tk()
    window.title('finding minimal paths')
    window.geometry("500x500")
    inputtxt = Text(window, height=2, width=20)
    inputtxt.place(x=100, y=430)
    lbl = Label(window, text="test")
    lbl.place(x=270, y=440)
    paths = glob.glob('./*.json')
    if not len(paths):
        print("No scenarios found!")
        return None
    scenario_path = paths[0][2:]

    plot(scenario_path=scenario_path, window=window, inputtxt=inputtxt, label=lbl)
    plot_button = Button(master=window,
                         command=lambda: plot(scenario_path=scenario_path, window=window, inputtxt=inputtxt, label=lbl),
                         height=2,
                         width=10,
                         text="Insert Solution")
    plot_button.place(x=17, y=430)

    window.mainloop()


if __name__ == "__main__":
    GUI()
