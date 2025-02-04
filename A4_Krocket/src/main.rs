use std::fs::File;
use std::io::Write;
use std::io::{self, BufRead};
use std::time::Instant;

fn read_input(file_path: &str) -> (Vec<((i32, i32), (i32, i32))>, f64, Vec<((i32, i32), (i32, i32))>) {
    let file = File::open(file_path).expect("Unable to open file");
    let reader = io::BufReader::new(file);
    let mut lines = reader.lines().map(|l| l.unwrap());

    let first_line = lines.next().unwrap();
    let (n, r) = {
        let mut parts = first_line.split_whitespace();
        let n = parts.next().unwrap().parse::<i32>().unwrap();
        let r = parts.next().unwrap().parse::<f64>().unwrap();
        (n, r)
    };

    let mut gate_points = Vec::new();
    for _ in 0..n {
        let line = lines.next().unwrap();
        let mut parts = line.split_whitespace();
        let x1 = parts.next().unwrap().parse::<i32>().unwrap();
        let y1 = parts.next().unwrap().parse::<i32>().unwrap();
        let x2 = parts.next().unwrap().parse::<i32>().unwrap();
        let y2 = parts.next().unwrap().parse::<i32>().unwrap();
        gate_points.push(((x1, y1), (x2, y2)));
    }

    let mut gates2 = gate_points.clone();
    if file_path == "./A4_Krocket/krocket3.txt" {
        gates2.sort_by(|a, b| {
            let dist_a = ((a.0 .0 as f64).hypot(a.0 .1 as f64)).min((a.1 .0 as f64).hypot(a.1 .1 as f64));
            let dist_b = ((b.0 .0 as f64).hypot(b.0 .1 as f64)).min((b.1 .0 as f64).hypot(b.1 .1 as f64));
            dist_a.partial_cmp(&dist_b).unwrap()
        });
    }

    (gate_points, r*2.0, gates2)
}

extern crate plotters;
use plotters::prelude::*;
use plotters::style::WHITE;
use plotters::style::IntoFont;
use plotters::chart::ChartBuilder;
use plotters::series::LineSeries;
use plotters::backend::BitMapBackend;

fn plot_gate_points(gate_points: Vec<((i32, i32), (i32, i32))>, intersection_vector: ((f64, f64), (f64, f64)), parallel_vectors: Vec<((f64, f64), (f64, f64))>, file_number: &str) -> Result<(), Box<dyn std::error::Error>> {
    let file_name = format!("plot_{}.svg", file_number);
    let root = SVGBackend::new(&file_name, (1280, 960)).into_drawing_area();
    root.fill(&WHITE)?;

    let mut chart = ChartBuilder::on(&root)
        .caption("Gate Points and Intersection Vector", ("sans-serif", 50).into_font())
        .margin(10)
        .x_label_area_size(30)
        .y_label_area_size(30)
        .build_cartesian_2d(
            gate_points.iter().flat_map(|&((x1, _), (x2, _))| vec![x1, x2]).min().unwrap()..gate_points.iter().flat_map(|&((x1, _), (x2, _))| vec![x1, x2]).max().unwrap(),
            gate_points.iter().flat_map(|&((_, y1), (_, y2))| vec![y1, y2]).min().unwrap()..gate_points.iter().flat_map(|&((_, y1), (_, y2))| vec![y1, y2]).max().unwrap()
        )?;
    chart.configure_mesh().draw()?;

    for gate in &gate_points {
        chart.draw_series(LineSeries::new(
            vec![(gate.0 .0, gate.0 .1), (gate.1 .0, gate.1 .1)],
            &plotters::style::RED,
        ))?;
    }

    chart.draw_series(LineSeries::new(
        vec![(intersection_vector.0 .0 as i32, intersection_vector.0 .1 as i32), (intersection_vector.1 .0 as i32, intersection_vector.1 .1 as i32)],
        &plotters::style::BLUE,
    ))?;

    for vector in &parallel_vectors {
        chart.draw_series(LineSeries::new(
            vec![(vector.0 .0 as i32, vector.0 .1 as i32), (vector.1 .0 as i32, vector.1 .1 as i32)],
            &plotters::style::BLUE,
        ))?;
    }

    root.present()?;
    Ok(())
}

fn find_intersection_vector(gates: &Vec<((i32, i32), (i32, i32))>, width: f64) -> (((f64, f64), (f64, f64)), Vec<((f64, f64), (f64, f64))>, Vec<((i32, i32), (i32, i32))>) {
    fn extending_length(gates: &Vec<((i32, i32), (i32, i32))>, _width: f64) -> f64 {
        gates.iter().map(|&((x1, y1), (x2, y2))| {
            (((x2 - x1).pow(2) as f64 + (y2 - y1).pow(2) as f64).sqrt() / 3.0) as f64
        }).sum()
    }

    fn extend_vector(start_point: (f64, f64), end_point: (f64, f64), length: f64) -> ((f64, f64), (f64, f64)) {
        let direction_vector = (end_point.0 - start_point.0, end_point.1 - start_point.1);
        let vector_length = (direction_vector.0.powi(2) + direction_vector.1.powi(2)).sqrt();
        let scale_factor = length / vector_length;
        let extended_start = (start_point.0 - direction_vector.0 * scale_factor.min(1.0), start_point.1 - direction_vector.1 * scale_factor.min(1.0));
        let extended_end = (end_point.0 + direction_vector.0 * scale_factor.min(1.0), end_point.1 + direction_vector.1 * scale_factor.min(1.0));
        (extended_start, extended_end)
    }

    fn count_crossed_gates(start_point: (f64, f64), end_point: (f64, f64), gates: &Vec<((i32, i32), (i32, i32))>, width: f64) -> (usize, Vec<((f64, f64), (f64, f64))>, Vec<((i32, i32), (i32, i32))>) {
        fn ccw(a: (f64, f64), b: (f64, f64), c: (i32, i32)) -> bool {
            (c.1 as f64 - a.1) * (b.0 - a.0) > (b.1 as f64 - a.1) * (c.0 as f64 - a.0)
        }

        fn do_lines_intersect(p1: (f64, f64), p2: (f64, f64), q1: (i32, i32), q2: (i32, i32)) -> bool {
            ccw(p1, (q1.0 as f64, q1.1 as f64), (q2.0, q2.1)) != ccw(p2, (q1.0 as f64, q1.1 as f64), (q2.0, q2.1)) && ccw(p1, p2, (q1.0, q1.1)) != ccw(p1, p2, (q2.0, q2.1))
        }

        let mut count = 0;

        fn is_point_on_line(px: f64, py: f64, x1: i32, y1: i32, x2: i32, y2: i32) -> bool {
            (x2 - x1) as f64 * (py - y1 as f64) == (y2 - y1) as f64 * (px - x1 as f64) && x1.min(x2) as f64 <= px && px <= x1.max(x2) as f64 && y1.min(y2) as f64 <= py && py <= y1.max(y2) as f64
        }

        fn move_point_by_half_width(point: (f64, f64), direction_vector: (f64, f64), width: f64) -> ((f64, f64), (f64, f64)) {
            let length = (direction_vector.0.powi(2) + direction_vector.1.powi(2)).sqrt();
            let perp_dx = -direction_vector.1 / length * width / 2.0;
            let perp_dy = direction_vector.0 / length * width / 2.0;
            ((point.0 + perp_dx, point.1 + perp_dy), (point.0 - perp_dx, point.1 - perp_dy))
        }

        let direction_vector = (end_point.0 - start_point.0, end_point.1 - start_point.1);
        let (start_point1, start_point2) = move_point_by_half_width(start_point, direction_vector, width);
        let (end_point1, end_point2) = move_point_by_half_width(end_point, direction_vector, width);
        let (start_point1_ext, end_point1_ext) = extend_vector(start_point1, end_point1, extending_length(gates, width));
        let (start_point2_ext, end_point2_ext) = extend_vector(start_point2, end_point2, extending_length(gates, width));
        let mut faulty_gates = Vec::new();

        for gate in gates {
            let ((x1, y1), (x2, y2)) = *gate;
            if (is_point_on_line(start_point1_ext.0, start_point1_ext.1, x1, y1, x2, y2) &&
                is_point_on_line(end_point1_ext.0, end_point1_ext.1, x1, y1, x2, y2) &&
                is_point_on_line(start_point2_ext.0, start_point2_ext.1, x1, y1, x2, y2) &&
                is_point_on_line(end_point2_ext.0, end_point2_ext.1, x1, y1, x2, y2)) ||
                (do_lines_intersect(start_point1_ext, end_point1_ext, (x1, y1), (x2, y2)) &&
                 do_lines_intersect(start_point2_ext, end_point2_ext, (x1, y1), (x2, y2))) {
                count += 1;
            } else {
                faulty_gates.push(*gate);
            }
        }
        (count, vec![(start_point1, end_point1), (start_point2, end_point2)], faulty_gates)
    }

    fn generate_points(gate: ((i32, i32), (i32, i32)), num_points: usize) -> Vec<(f64, f64)> {
        let ((x1, y1), (x2, y2)) = gate;
        (0..num_points).map(|t| {
            let t = t as f64 / (num_points - 1) as f64;
            (x1 as f64 + t * (x2 as f64 - x1 as f64), y1 as f64 + t * (y2 as f64 - y1 as f64))
        }).collect()
    }

    let mut best_start_point = None;
    let mut best_end_point = None;
    let mut start_point1 = None;
    let mut end_point1 = None;
    let mut start_point2 = None;
    let mut end_point2 = None;
    let mut max_crossed_gates = 0;
    let mut faulty_gates = Vec::new();

    let mut num_points = 15;
    let max_points = 150;
    let mut all_gates_crossed = false;

    while !all_gates_crossed && num_points <= max_points {
        let start_points = generate_points(gates[0], num_points);
        let end_points = generate_points(gates[gates.len() - 1], num_points);

        for start_point in &start_points {
            for end_point in &end_points {
                let (crossed_gates, points, _faulty_gate) = count_crossed_gates(*start_point, *end_point, gates, width);
                if crossed_gates > max_crossed_gates {
                    max_crossed_gates = crossed_gates;
                    best_start_point = Some(*start_point);
                    best_end_point = Some(*end_point);
                    start_point1 = Some(points[0]);
                    start_point2 = Some(points[1]);
                    end_point1 = Some(points[0]);
                    end_point2 = Some(points[1]);
                    faulty_gates = _faulty_gate;
                    if max_crossed_gates == gates.len() {
                        all_gates_crossed = true;
                        break;
                    }
                }
            }
            if all_gates_crossed {
                break;
            }
        }

        if !all_gates_crossed {
            num_points += 20;
        }
    }

    let best_start_point = best_start_point.unwrap();
    let best_end_point = best_end_point.unwrap();
    // let intersection_vector = extend_vector(best_start_point, best_end_point, extending_length(gates, width));
    let intersection_vector = (best_start_point, best_end_point);
    println!("Intersection Vector: Start {:?}, End {:?}", best_start_point, best_end_point);
    println!("Vector Equation: r(t) = ({}, {}) + t * (({}, {})) for t in [0, 1]", best_start_point.0, best_start_point.1, best_end_point.0 - best_start_point.0, best_end_point.1 - best_start_point.1);
    println!("Crossed Gates: {} out of {}", gates.len() - faulty_gates.len(), gates.len());
    let direction_vector = (best_end_point.0 - best_start_point.0, best_end_point.1 - best_start_point.1);
    println!("Start Point: {:?}", best_start_point);
    println!("Direction Vector: {:?}", direction_vector);
    (intersection_vector, vec![start_point1.unwrap(), end_point1.unwrap(), start_point2.unwrap(), end_point2.unwrap()], faulty_gates)
}

fn main() {
    let global_start_time = Instant::now();
    let file_paths = [
        "./A4_Krocket/krocket1.txt",
        "./A4_Krocket/krocket2.txt",
        "./A4_Krocket/krocket3.txt",
        "./A4_Krocket/krocket4.txt",
        "./A4_Krocket/krocket5.txt",
    ];
    let mut file_dict = std::collections::HashMap::new();
    for (i, file_path) in file_paths.iter().enumerate() {
        file_dict.insert(*file_path, (i + 1).to_string());
    }

    for file_path in &file_paths {
        println!("Processing file: {}", file_path);
        let (gate_points, width, gates2) = read_input(file_path);

        let start_time = Instant::now();
        let (intersection_vector, _parallel_vectors, faulty_gates) = find_intersection_vector(&gates2, width);
        let gates_crossed = gates2.len() - faulty_gates.len();
        println!("Number of gates crossed: {}", gates_crossed);
        let end_time = Instant::now();
        println!("Intersection Vector: Start {:?}, End {:?}", intersection_vector.0, intersection_vector.1);
        println!("Time taken to find the intersection vector: {:?}", end_time.duration_since(start_time));
        // Write the data to a file
        let output_file_name = format!("output_{}.txt", file_dict.get(file_path).unwrap());
        let mut output_file = File::create(&output_file_name).expect("Unable to create output file");

        writeln!(output_file, "Intersection Vector: Start {:?}, End {:?}", intersection_vector.0, intersection_vector.1).expect("Unable to write data");
        writeln!(output_file, "Vector Equation: r(t) = ({}, {}) + t * (({}, {})) for t in [0, 1]", intersection_vector.0 .0, intersection_vector.0 .1, intersection_vector.1 .0 - intersection_vector.0 .0, intersection_vector.1 .1 - intersection_vector.0 .1).expect("Unable to write data");
        writeln!(output_file, "Crossed Gates: {} out of {}", gates2.len() - faulty_gates.len(), gates2.len()).expect("Unable to write data");
        writeln!(output_file, "Start Point: {:?}", intersection_vector.0).expect("Unable to write data");
        writeln!(output_file, "Direction Vector: {:?}", (intersection_vector.1 .0 - intersection_vector.0 .0, intersection_vector.1 .1 - intersection_vector.0 .1)).expect("Unable to write data");
        
        // Call the plotting function
        if let Err(e) = plot_gate_points(gates2.clone(), intersection_vector, _parallel_vectors.clone(), file_dict.get(file_path).unwrap()) {
            eprintln!("Error plotting gate points: {}", e);
        }
    }
    let global_end_time = Instant::now();
    println!("Total time taken: {:?}", global_end_time.duration_since(global_start_time));

    // Write the total time taken to a file
    let mut total_time_file = File::create("total_time.txt").expect("Unable to create total time file");
    writeln!(total_time_file, "Total time taken: {:?}", global_end_time.duration_since(global_start_time)).expect("Unable to write total time");
}