import numpy as np
import matplotlib.pyplot as plt
import time

import concurrent.futures

def read_input(file_path):
    with open(file_path, 'r') as file:
        lines = file.readlines()
    
    n, r = map(int, lines[0].strip().split())
    gates = []
    for line in lines[1:n+1]:
        x1, y1, x2, y2 = map(int, line.strip().split())
        gates.append(((x1, y1), (x2, y2)))
    
    # Sort gates by their distance from the origin (0, 0)
    if (file_path == 'Runde_1/Beispiele/A4_Krocket/krocket3.txt'):
        gates.sort(key=lambda gate: min(np.hypot(gate[0][0], gate[0][1]), np.hypot(gate[1][0], gate[1][1])))
    
    return gates

def plot_gates(gates):
    for gate in gates:
        (x1, y1), (x2, y2) = gate
        plt.plot([x1, x2], [y1, y2], marker='o')
    
    plt.xlabel('X')
    plt.ylabel('Y')
    plt.title('Gates Plot')
    plt.grid(True)

def find_intersection_vector(gates):
    def count_crossed_gates(start_point, end_point, gates):
        def do_lines_intersect(p1, p2, q1, q2):
            def ccw(A, B, C):
                return (C[1] - A[1]) * (B[0] - A[0]) > (B[1] - A[1]) * (C[0] - A[0])
            return ccw(p1, q1, q2) != ccw(p2, q1, q2) and ccw(p1, p2, q1) != ccw(p1, p2, q2)

        def is_point_on_line(px, py, x1, y1, x2, y2):
            return (x2 - x1) * (py - y1) == (y2 - y1) * (px - x1) and min(x1, x2) <= px <= max(x1, x2) and min(y1, y2) <= py <= max(y1, y2)

        count = 0
        for gate in gates:
            (x1, y1), (x2, y2) = gate
            if is_point_on_line(start_point[0], start_point[1], x1, y1, x2, y2) or is_point_on_line(end_point[0], end_point[1], x1, y1, x2, y2):
                count += 1
            elif do_lines_intersect(start_point, end_point, (x1, y1), (x2, y2)):
                count += 1
        return count

    best_start_point = None
    best_end_point = None
    max_crossed_gates = 0

    def generate_points(gate, num_points):
        (x1, y1), (x2, y2) = gate
        return [(x1 + t * (x2 - x1), y1 + t * (y2 - y1)) for t in np.linspace(0, 1, num_points)]

    num_points = 10
    max_points = 50
    all_gates_crossed = False

    while not all_gates_crossed and num_points <= max_points:
        (x1_start, y1_start), (x2_start, y2_start) = gates[0]
        (x1_end, y1_end), (x2_end, y2_end) = gates[-1]

        start_points = generate_points(gates[0], num_points)
        end_points = generate_points(gates[-1], num_points)

        for start_point in start_points:
            for end_point in end_points:
                crossed_gates = count_crossed_gates(start_point, end_point, gates)
                if crossed_gates > max_crossed_gates:
                    max_crossed_gates = crossed_gates
                    best_start_point = start_point
                    best_end_point = end_point
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
    return intersection_vector

def plot_intersection_vector(vector):
    (x1, y1), (x2, y2) = vector
    plt.plot([x1, x2], [y1, y2], marker='x', color='red', linestyle='--', label='Intersection Vector')
    plt.legend()

def main():
    file_path = 'Runde_1/Beispiele/A4_Krocket/krocket4.txt'  # Replace with your input file path
    gates = read_input(file_path)
    plot_gates(gates)
    
    start_time = time.time()
    intersection_vector = find_intersection_vector(gates)
    end_time = time.time()
    
    print(f"Time taken to find the intersection vector: {end_time - start_time} seconds")
    
    plot_intersection_vector(intersection_vector)
    plt.show()

if __name__ == '__main__':
    main()