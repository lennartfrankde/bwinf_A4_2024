import numpy as np
import matplotlib.pyplot as plt
import time

import concurrent.futures

def read_input(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    n, r = map(int, lines[0].strip().split())
    gatePoints = []
    for line in lines[1:n+1]:
        x1, y1, x2, y2 = map(int, line.strip().split())
        gatePoints.append(((x1, y1), (x2, y2)))
    # Sort gates by their distance from the origin (0, 0)
    gates2 = gatePoints
    if (file_path == 'Runde_1/Beispiele/A4_Krocket/krocket3.txt'):
        gates2.sort(key=lambda gate: min(np.hypot(gate[0][0], gate[0][1]), np.hypot(gate[1][0], gate[1][1])))
    return gatePoints, r*2, gates2

def plot_gates(gates):
    for gate in gates:
        (x1, y1), (x2, y2) = gate
        plt.plot([x1, x2], [y1, y2])
    
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Gates Plot')
    plt.grid(True)

def plot_r_gates(lines):
    for n in range(len(lines)):
        (x1, y1), (x2, y2) = lines[n]
        if n == 0 or n == len(lines) - 1:
            plt.plot([x1, x2], [y1, y2], color='red', marker='o')
        else:
            plt.plot([x1, x2], [y1, y2], color='gray')
    
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Gates Plot')
    plt.grid(True)

def plot_faulty_gates(lines):
    for n in range(len(lines)):
        (x1, y1), (x2, y2) = lines[n]
        plt.plot([x1, x2], [y1, y2], color='orange', marker='o')



def find_intersection_vector(gates, width=1.0, setY = False):
    def extending_length(gates, width):
        length = 0
        (x1, y1), (x2, y2) = gates[0]
        length += np.hypot(x2 - x1, y2 - y1)
        return length/3
    def extend_vector(start_point, end_point, length):
        direction_vector = (end_point[0] - start_point[0], end_point[1] - start_point[1])
        vector_length = np.hypot(direction_vector[0], direction_vector[1])
        scale_factor = length / vector_length
        extended_start = (start_point[0] - direction_vector[0] * scale_factor, start_point[1] - direction_vector[1] * scale_factor)
        extended_end = (end_point[0] + direction_vector[0] * scale_factor, end_point[1] + direction_vector[1] * scale_factor)
        return extended_start, extended_end
    def count_crossed_gates(start_point, end_point, gates, width):
        def do_lines_intersect(p1, p2, q1, q2):
            def ccw(A, B, C):
                return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
            return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)

        def is_point_on_line(px, py, x1, y1, x2, y2):
            return (x2 - x1) * (py - y1) == (y2 - y1) * (px - x1) and min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2)
        
        def move_point_by_half_width(point, direction_vector, width):
            length = np.hypot(direction_vector[0], direction_vector[1])
            perp_dx, perp_dy = -direction_vector[1] / length * width / 2, direction_vector[0] / length * width / 2
            return (point[0] + perp_dx, point[1] + perp_dy), (point[0] - perp_dx, point[1] - perp_dy)

        count = 0
        direction_vector = (end_point[0] - start_point[0], end_point[1] - start_point[1])
        start_point1, start_point2 = move_point_by_half_width(start_point, direction_vector, width)
        end_point1, end_point2 = move_point_by_half_width(end_point, direction_vector, width)
        start_point1, end_point1 = extend_vector(start_point1, end_point1, extending_length(gates, width))
        start_point2, end_point2 = extend_vector(start_point2, end_point2, extending_length(gates, width))
        faulty_gates = []
        for gate in gates:
            (x1, y1), (x2, y2) = gate
            if ((is_point_on_line(start_point1[0], start_point1[1], x1, y1, x2, y2) and
                 is_point_on_line(end_point1[0], end_point1[1], x1, y1, x2, y2) and
                 is_point_on_line(start_point2[0], start_point2[1], x1, y1, x2, y2) and
                 is_point_on_line(end_point2[0], end_point2[1], x1, y1, x2, y2)) or
                (do_lines_intersect(start_point1, end_point1, (x1, y1), (x2, y2)) and
                 do_lines_intersect(start_point2, end_point2, (x1, y1), (x2, y2)))):
                count += 1
            else:
                faulty_gates.append(gate)
        return count, [start_point1, end_point1, start_point2, end_point2], faulty_gates

    best_start_point = None
    best_end_point = None
    start_point1 = None
    end_point1 = None
    start_point2 = None
    end_point2 = None
    max_crossed_gates = 0
    faulty_gates = []

    def generate_points(gate, num_points):
        (x1, y1), (x2, y2) = gate
        return [(x1 + t * (x2 - x1), y1 + t * (y2 - y1)) for t in np.linspace(0, 1, num_points)]

    num_points = 15
    max_points = 150
    all_gates_crossed = False

    while not all_gates_crossed and num_points <= max_points:
        (x1_start, y1_start), (x2_start, y2_start) = gates[0]
        (x1_end, y1_end), (x2_end, y2_end) = gates[-1]

        start_points = generate_points(gates[0], num_points)
        # print(start_points)
        end_points = generate_points(gates[-1], num_points)

        for start_point in start_points:
            for end_point in end_points:
                crossed_gates, points, faulty_gate = count_crossed_gates(start_point, end_point, gates, width)
                if crossed_gates > max_crossed_gates:
                    max_crossed_gates = crossed_gates
                    best_start_point = start_point
                    best_end_point = end_point
                    start_point1, end_point1, start_point2, end_point2 = points
                    faulty_gates = faulty_gate
                    if max_crossed_gates == len(gates):
                        all_gates_crossed = True
                        break
            if all_gates_crossed:
                break

        if not all_gates_crossed:
            num_points += 20 # Increase the number of points to check

    # Create a vector from the best start point to the best end point
    intersection_vector = [best_start_point, best_end_point]
    print(f"Intersection Vector: Start {best_start_point}, End {best_end_point}")
    print(f"Vector Equation: r(t) = ({best_start_point[0]}, {best_start_point[1]}) + t * (({best_end_point[0] - best_start_point[0]}, {best_end_point[1] - best_start_point[1]}) for t in [0, 1]")
    print(f"Crossed Gates: {max_crossed_gates} out of {len(gates)}")
    direction_vector = (best_end_point[0] - best_start_point[0], best_end_point[1] - best_start_point[1])
    print(f"Start Point: {best_start_point}")
    print(f"Direction Vector: {direction_vector}")
    # return intersection_vector
    return extend_vector(best_start_point, best_end_point, extending_length(gates, width)), [[start_point1, end_point1], [start_point2, end_point2]], faulty_gates

def plot_intersection_vector(vector, width, gates):
    (x1, y1), (x2, y2) = vector
    plt.plot([x1, x2], [y1, y2], marker='x', color='red', linestyle='--', label='Intersection Vector')

    dx, dy = x2 - x1, y2 - y1
    length = np.hypot(dx, dy)
    perp_dx, perp_dy = -dy / length * width*0.5, dx / length * width*0.5

    # Create the polygon for the width area
    polygon_points = [
        (x2 + perp_dx, y2 + perp_dy),
        (x2 - perp_dx, y2 - perp_dy),
        (x1 - perp_dx, y1 - perp_dy),
        (x1 + perp_dx, y1 + perp_dy),
    ]
    polygon = plt.Polygon(polygon_points, color='blue', alpha=0.3, label='Width Area')
    plt.gca().add_patch(polygon)

    plt.legend()

def plot_paralell_vector(vector):
    (x1, y1), (x2, y2) = vector
    plt.plot([x1, x2], [y1, y2], marker='x', color='green', linestyle='--', label='Intersection Vector')
    plt.legend()

def main():
    global_start_time = time.time()
    file_paths = [
        'Runde_1/Beispiele/A4_Krocket/krocket1.txt',
        'Runde_1/Beispiele/A4_Krocket/krocket2.txt',
        'Runde_1/Beispiele/A4_Krocket/krocket3.txt',
        'Runde_1/Beispiele/A4_Krocket/krocket4.txt',
        'Runde_1/Beispiele/A4_Krocket/krocket5.txt'
    ]

    file_paths_num = {
        'Runde_1/Beispiele/A4_Krocket/krocket1.txt': 1,
        'Runde_1/Beispiele/A4_Krocket/krocket2.txt': 2,
        'Runde_1/Beispiele/A4_Krocket/krocket3.txt': 3,
        'Runde_1/Beispiele/A4_Krocket/krocket4.txt': 4,
        'Runde_1/Beispiele/A4_Krocket/krocket5.txt': 5
    }
    
    for file_path in file_paths:
        print(f"Processing file: {file_path}")
        gatePoints, width, gates2 = read_input(file_path)
        plot_r_gates(gates2)
        print(f"Width: {width}")
        start_time = time.time()
        intersection_vector, paralell_vectors, faulty_gates = find_intersection_vector(gates2, width)
        end_time = time.time()
        
        print(f"Time taken to find the intersection vector: {end_time - start_time} seconds")
        
        plot_intersection_vector(intersection_vector, width, gates2)
        plot_paralell_vector(paralell_vectors[0])
        plot_paralell_vector(paralell_vectors[1])
        plot_faulty_gates(faulty_gates)
        plt.savefig(f"Runde_1/Beispiele/A4_Krocket/krocket_plot_{file_paths_num.get(file_path)}.svg", format='svg')
        plt.clf()
    global_end_time = time.time()
    print(f"Total time taken: {global_end_time - global_start_time} seconds")

if __name__ == '__main__':
    main()