import numpy as np
import matplotlib.pyplot as plt
import os.path
import json


def distance(P1, P2):
    return ((P1[0] - P2[0]) ** 2 + (P1[1] - P2[1]) ** 2) ** 0.5


def round_num(x):
    return int(100 * x) / 100


def error(d):
    return np.random.normal(d, 1)


def generate_scenario(polygons_number=5, vertices_max_number=8, circles_number=5, radius_max=4,
                      source=[0, 0], target=[15, 15]):
    final_dict = {"source": source, "target": target}
    polygons = []
    for _ in range(polygons_number):
        center_x = round_num(np.random.uniform(2, 15))
        center_y = round_num(np.random.uniform(3, 12))
        theta0 = np.random.uniform(0, np.pi / 2)
        polygon = []
        k = np.random.randint(3, vertices_max_number)
        d1 = np.random.uniform(1, 4)
        d2 = np.random.uniform(1, 4)
        for j in range(k):
            polygon.append(
                [round_num(center_x + d1 * np.cos(theta0 + 2 * np.pi * j / k)),
                 round_num(center_y + d2 * np.sin(theta0 + 2 * np.pi * j / k))])
        polygons.append(polygon)
    circles = []
    for _ in range(circles_number):
        center = [round_num(np.random.uniform(-2, 17)), round_num(np.random.uniform(-2, 17))]
        radius = round_num(np.random.uniform(0, radius_max))
        while distance(center, source) <= radius or distance(center, target) <= radius:
            center = [round_num(np.random.uniform(-2, 17)), round_num(np.random.uniform(-2, 17))]
        circle = [center, radius]
        circles.append(circle)
    final_dict["polygons"] = polygons
    final_dict["circles"] = circles
    num = 1
    prefix_path = os.path.normpath(os.getcwd() + os.sep + os.pardir)
    scenarios_path = "prom\scenarios\scenario_"
    GUI_path = "prom\GUI\scenario_"
    while os.path.isfile(scenarios_path + str(num) + ".json"):
        num += 1
    with open(scenarios_path + str(num) + ".json", "w+") as file:
        json.dump(final_dict, file)
    with open(GUI_path + str(num) + ".json", "w+") as file:
        json.dump(final_dict, file)
    os.remove(GUI_path + str(num - 1) + ".json")
    return None


def draw_polygon(points_list):
    n = len(points_list)
    for i in range(n - 1):
        plt.plot(points_list[i], points_list[i + 1], "ro-")
    plt.plot(points_list[n - 1], points_list[0], "ro-")
    plt.show()


if __name__ == "__main__":
    generate_scenario(polygons_number=3, circles_number=3, vertices_max_number=10, radius_max=4)
