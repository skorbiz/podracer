use std::io;

#[derive(Clone, Copy, Debug)]
struct Pod {
    x: i32,
    y: i32,
    theta: i32,
}

struct Checkpoint {
    x: i32,
    y: i32,
    distance: i32,
    theta: i32,
}

#[derive(Debug)]
enum Power {
    Boost,
    Shield,
}

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

fn parse_pods(input: &str) -> Option<[Pod; 2]> {
    let variables: Vec<&str> = input.split_whitespace().collect();
    if variables.len() != 6 {
        return None;
    }

    let x1 = variables[0].parse::<i32>();
    let y1 = variables[1].parse::<i32>();
    let t1 = variables[2].parse::<i32>();
    let x2 = variables[3].parse::<i32>();
    let y2 = variables[4].parse::<i32>();
    let t2 = variables[5].parse::<i32>();

    if x1.is_ok() && y1.is_ok() && t1.is_ok() && x2.is_ok() && y2.is_ok() && t2.is_ok() {
        return Some([
            Pod {
                x: x1.unwrap(),
                y: y1.unwrap(),
                theta: t1.unwrap(),
            },
            Pod {
                x: x2.unwrap(),
                y: y2.unwrap(),
                theta: t2.unwrap(),
            },
        ]);
    }

    None
}

fn parse_checkpoint(input: &str) -> Option<Checkpoint> {
    let variables: Vec<&str> = input.split_whitespace().collect();
    if variables.len() != 4 {
        return None;
    }

    let x = variables[0].parse::<i32>();
    let y = variables[1].parse::<i32>();
    let distance = variables[2].parse::<i32>();
    let theta = variables[3].parse::<i32>();

    if x.is_ok() && y.is_ok() && distance.is_ok() && theta.is_ok() {
        return Some(Checkpoint {
            x: x.unwrap(),
            y: y.unwrap(),
            distance: distance.unwrap(),
            theta: theta.unwrap(),
        });
    }

    None
}

fn parse_enemies(input: &str) -> Vec<Pod> {
    let mut enemies = vec![];

    let variables: Vec<&str> = input.split_whitespace().collect();
    if variables.len() % 3 != 0 {
        return enemies;
    }

    for i in (0..variables.len()).step_by(3) {
        let x = variables[i + 0].parse::<i32>();
        let y = variables[i + 1].parse::<i32>();
        let theta = variables[i + 2].parse::<i32>();
        if x.is_ok() && y.is_ok() && theta.is_ok() {
            enemies.push(Pod {
                x: x.unwrap(),
                y: y.unwrap(),
                theta: theta.unwrap(),
            });
        }
    }

    enemies
}

fn main_loop() {
    let mut inputs: [String; 4] = [String::new(), String::new(), String::new(), String::new()];
    for i in 0..4 {
        io::stdin()
            .read_line(inputs.get_mut(i).unwrap())
            .unwrap_or(0);
    }
    // eprintln!("Pod: {}", inputs[0]);
    // eprintln!("Objectives: {}", inputs[1]);
    // eprintln!("Enemy: {}", inputs[2]);
    // eprintln!("Friendlies: {}", inputs[3]);

    let pod = parse_pod(inputs.get(0).unwrap());
    let pods = parse_pods(inputs.get(0).unwrap());
    let checkpoint = parse_checkpoint(inputs.get(1).unwrap());
    let enemies = parse_enemies(inputs.get(2).unwrap());

    if pods.is_none() {
        println!("{} {} {} {} {} {}", 8000, 4500, 100, 8000, 4500, 100);
    }

    let pods = pods.unwrap();

    let racer = plan_racer(&pods[0], &checkpoint);
    let guard = plan_guard(&pods[1], &pods[0], &enemies);
    drive_two_pods(racer, guard);
}

fn main() {
    let mut buffer = String::new();
    io::stdin().read_line(&mut buffer).unwrap_or(0);

    match buffer.as_str() {
        "RACE" => {}
        "ELIMINATION" => {}
        _ => {}
    }

    loop {
        main_loop();
    }
}

fn drive(x: i32, y: i32, thrust: i32) {
    println!("{} {} {}", x, y, thrust);
}

fn drive_two_pods(racer: Control, guard: Control) {
    let racer_thrust = match racer.power {
        Some(Power::Boost) => "BOOST".to_string(),
        Some(Power::Shield) => "SHIELD".to_string(),
        None => racer.thrust.to_string(),
    };
    let guard_thrust = match guard.power {
        Some(Power::Boost) => "BOOST".to_string(),
        Some(Power::Shield) => "SHIELD".to_string(),
        None => guard.thrust.to_string(),
    };
    println!(
        "{} {} {} {} {} {}",
        racer.x, racer.y, racer_thrust, guard.x, guard.y, guard_thrust
    );
}

fn plan(pod: &Option<Pod>, checkpoint: &Option<Checkpoint>) {
    let cp = checkpoint.as_ref().unwrap();
    let dist: f32 = cp.distance as f32;
    // let thrust = (dist - 300.0).powi(5) as i32;
    let thrust_offset = 25;
    let thrust = dist.sqrt() as i32 + thrust_offset;
    eprintln!("Thrust: {}", thrust);
    drive(cp.x, cp.y, thrust)
}

fn plan_racer(pod: &Pod, checkpoint: &Option<Checkpoint>) -> Control {
    let cp = checkpoint.as_ref().unwrap();
    let dist: f32 = cp.distance as f32;
    // let thrust = (dist - 300.0).powi(5) as i32;
    let thrust_offset = 25;
    let thrust = dist.sqrt() as i32 + thrust_offset;
    let thrust_distance = 10000;
    let shield_distance = 6000;
    let trigger_distance = 100;
    let power = if cp.distance > (thrust_distance - trigger_distance)
        && cp.distance < (thrust_distance + trigger_distance)
    {
        Some(Power::Boost)
    } else if cp.distance > (shield_distance - trigger_distance)
        && cp.distance < (shield_distance + trigger_distance)
    {
        Some(Power::Shield)
    } else {
        None
    };
    eprintln!("Thrust: {}", thrust);
    eprintln!("{:?}", power);
    Control {
        x: cp.x,
        y: cp.y,
        thrust,
        power,
    }
}

fn find_the_enemy(guard: &Pod, racer: &Pod, enemies: &Vec<Pod>) -> Option<Pod> {
    let mut target: Option<Pod> = None;
    let mut closest_dist: Option<i32> = None;

    for enemy in enemies.iter() {
        let dx = enemy.x - racer.x;
        let dy = enemy.y - racer.y;
        let dist_sq = ((dx.pow(2) + dy.pow(2)) as f32).sqrt() as i32;
        if closest_dist.is_none() {
            target = Some(enemy.clone());
        } else {
            if dist_sq < closest_dist.unwrap() {
                target = Some(enemy.clone());
                closest_dist = Some(dist_sq);
            }
        }
    }

    return target;
}

fn find_the_closest(guard: &Pod, racer: &Pod, enemies: &Vec<Pod>) -> Option<Pod> {
    let mut target: Option<Pod> = None;
    let mut closest_dist: Option<i32> = None;

    for enemy in enemies.iter() {
        let dx = enemy.x - guard.x;
        let dy = enemy.y - guard.y;
        let dist_sq = dx.pow(2) + dy.pow(2);
        if closest_dist.is_none() {
            target = Some(enemy.clone());
        } else {
            if dist_sq < closest_dist.unwrap() {
                target = Some(enemy.clone());
                closest_dist = Some(dist_sq);
            }
        }
    }

    return target;
}

fn plan_guard(pod: &Pod, racer: &Pod, enemies: &Vec<Pod>) -> Control {
    let cp = find_the_enemy(pod, racer, enemies);
    eprintln!("Racer: {:?}", racer);
    eprintln!("Enemy: {:?}", cp);
    if cp.is_none() {
        return Control {
            x: 50,
            y: 50,
            thrust: 50,
            power: None,
        };
    }
    let dist_pw: i32 = cp.unwrap().x.pow(2) + cp.unwrap().y.pow(2);
    let dist: f32 = (dist_pw as f32).sqrt();

    let mut power: Option<Power> = None;
    let closest = find_the_closest(pod, racer, enemies);
    let cl_dist_pw: i32 = closest.unwrap().x.pow(2) + closest.unwrap().y.pow(2);
    let cl_dist: f32 = (cl_dist_pw as f32).sqrt();
    if cl_dist < 900.0 {
        power = Some(Power::Shield);
    }

    // let thrust = (dist - 300.0).powi(5) as i32;
    let thrust_offset = 25;
    let thrust = dist.sqrt() as i32 + thrust_offset;
    eprintln!("Thrust: {}", thrust);

    Control {
        x: cp.unwrap().x,
        y: cp.unwrap().y,
        thrust: thrust,
        power: power,
    }
}
