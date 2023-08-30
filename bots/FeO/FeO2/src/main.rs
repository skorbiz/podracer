use std::io;

#[derive(Clone, Copy, Debug)]
struct Pod {
    x: i32,
    y: i32,
    theta: i32,
}

struct Ball {
    x: i32,
    y: i32,
}

#[derive(Debug)]
enum Power {
    Boost,
    Shield,
}

#[derive(Debug)]
struct Control {
    x: i32,
    y: i32,
    thrust: i32,
    power: Option<Power>,
}

fn parse_pod(input: &str) -> Option<Pod> {
    let variables: Vec<&str> = input.split_whitespace().collect();
    if variables.len() != 3 {
        return None;
    }

    let x = variables[0].parse::<i32>();
    let y = variables[1].parse::<i32>();
    let theta = variables[2].parse::<i32>();

    if x.is_ok() && y.is_ok() && theta.is_ok() {
        return Some(Pod {
            x: x.unwrap(),
            y: y.unwrap(),
            theta: theta.unwrap(),
        });
    }

    None
}

fn parse_ball(input: &str) -> Option<Ball> {
    let variables: Vec<&str> = input.split_whitespace().collect();
    if variables.len() != 2 {
        return None;
    }

    let x = variables[0].parse::<i32>();
    let y = variables[1].parse::<i32>();

    if x.is_ok() && y.is_ok() {
        return Some(Ball {
            x: x.unwrap(),
            y: y.unwrap(),
        });
    }

    None
}

fn main_loop(wait_pos: (i32, i32)) {
    let mut inputs: [String; 4] = [String::new(), String::new(), String::new(), String::new()];
    for i in 0..4 {
        io::stdin()
            .read_line(inputs.get_mut(i).unwrap())
            .unwrap_or(0);
    }
    eprintln!("Pod: {}", inputs[0]);
    eprintln!("Objectives: {}", inputs[1]);
    // eprintln!("Enemy: {}", inputs[2]);
    // eprintln!("Friendlies: {}", inputs[3]);

    let pod = parse_pod(inputs.get(0).unwrap()).unwrap();
    let ball = parse_ball(inputs.get(1).unwrap()).unwrap();

    let control = plan_goalkeeper(pod, ball, wait_pos);

    drive_goalkeeper(control);
}

fn drive_goalkeeper(pod: Control) {
    let thrust = match pod.power {
        Some(Power::Boost) => "BOOST".to_string(),
        Some(Power::Shield) => "SHIELD".to_string(),
        None => pod.thrust.to_string(),
    };
    println!("{} {} {}", pod.x, pod.y, thrust);
}

fn plan_goalkeeper(pod: Pod, ball: Ball, wait_pos: (i32, i32)) -> Control {
    let dist_to_ball = (((ball.x - pod.x).pow(2) + (ball.y - pod.y).pow(2)) as f32).sqrt();
    let ball_to_goal =
        (((ball.x - wait_pos.0).pow(2) + (ball.y - wait_pos.1).pow(2)) as f32).sqrt();
    let dist_to_origin =
        (((wait_pos.0 - pod.x).pow(2) + (wait_pos.1 - pod.y).pow(2)) as f32).sqrt();
    let ball_to_keeper_angle =
        ((((ball.y - pod.y) as f32) / ((ball.x - pod.x) as f32) as f32).atan() * 180.0 / 3.1416)
            as i32;
    eprintln!("Angle: {}", ball_to_keeper_angle);

    if ball_to_goal < 4000.0 {
        if (pod.theta - ball_to_keeper_angle).abs() < 5 {
            eprintln!("Ball close");
            Control {
                x: ball.x,
                y: ball.y,
                thrust: 100,
                power: Some(Power::Boost),
            }
        } else {
            if dist_to_origin > 400.0 {
                Control {
                    x: wait_pos.0,
                    y: wait_pos.1,
                    thrust: ((dist_to_origin - 400.0).sqrt() as i32) + 5,
                    power: None,
                }
            } else {
                Control {
                    x: ball.x,
                    y: ball.y,
                    thrust: 1,
                    power: None,
                }
            }
        }
    } else if dist_to_origin > 400.0 {
        eprintln!("Far from home");
        Control {
            x: wait_pos.0,
            y: wait_pos.1,
            thrust: ((dist_to_origin - 400.0).sqrt() as i32) + 5,
            power: None,
        }
    } else {
        eprintln!("Waiting");
        Control {
            x: ball.x,
            y: ball.y,
            thrust: 1,
            power: None,
        }
    }
}

fn main() {
    let mut buffer = String::new();
    io::stdin().read_line(&mut buffer).unwrap_or(0);

    let mut inputs: [String; 4] = [String::new(), String::new(), String::new(), String::new()];
    for i in 0..4 {
        io::stdin()
            .read_line(inputs.get_mut(i).unwrap())
            .unwrap_or(0);
    }

    let pod = parse_pod(inputs.get(0).unwrap()).unwrap();
    let wait_pos = if pod.x < 8000 {
        (1000, 4500)
    } else {
        (15000, 4500)
    };

    println!("0 0 0");

    loop {
        main_loop(wait_pos);
    }
}
