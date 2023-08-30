import sys
import math
import numpy

def distance(p1, p2):
    dx = (p1[0]-p2[0])**2
    dy = (p1[1]-p2[1])**2

    return numpy.sqrt(dx + dy)

def get_guard_thrust(dist):
    guard_thrust = 100

    if guard_dist < 2000:
        guard_thrust = 50
    if guard_dist < 1000:
        guard_thrust = 20
    if guard_dist < 100:
        guard_thrust = 0

    return guard_thrust





# Gamemode is either RACE, FOOTBALL, ELEMINATION
gamemode = input()
print("The gamemode: {}".format(gamemode), file=sys.stderr, flush=True)


import random
enemy_target = random.randint(0, 10)
randomness = random.randint(0, 50)
i = 0
dist_log = {}
#distances = {goal: boost}
max_dist = 0
targets = []
second_round = False
boost_i = 0
first_boost = True

checkpoints = []



# game loop
while True:

    # pod_state: [x1, y1, theta1] or [x1, y1, theta1, x2, y2, theta2]
    # objectives: [next_checkpoint_x, next_checkpoint_y] for RACE, [] for ELEMINATION or [ball_x, ball_y] for FOOTBALL
    # enemy_pods: [enemy_x1, enemy_y1, enemy_theta1, enemy_x2, enemy_y2, enemy_theta2, ...]
    # friendly_pods: [friend_x1, friend_y1, friend_theta1, friend_x2, friend_y2, friend_theta2, ...]
    pod_states = [int(i) for i in input().split()]
    objectives = [int(i) for i in input().split()]
    enemy_pods = [int(i) for i in input().split()]
    friendly_pods = [int(i) for i in input().split()]

    if i == 0:
        new_goal = False
        old_x, old_y = pod_states[0], pod_states[1]

    # check for new objective, then full speed
    if not (old_x == objectives[0] and old_y == objectives[1]):
        new_goal = True
        x = objectives[0]
        y = objectives[1]
        print("---- New goal: {}, {}".format(objectives[0], objectives[1]), file=sys.stderr, flush=True)
        full_dist = math.sqrt((old_x - x)**2 + (old_y - y)**2)
        goal = "{}{}".format(x,y)
        if goal not in targets:
            targets.append(goal)
            if full_dist > max_dist:
                max_dist = full_dist
                boost_target = goal
        else:
            second_round = True

    old_x, old_y = objectives[0], objectives[1]

    target_x = 5000
    target_y = 5000
    if gamemode == 'RACE':
        next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = objectives
        target_x = next_checkpoint_x
        target_y = next_checkpoint_y

    if gamemode == 'FOOTBALL':
        football_x, football_y = objectives
        target_x = football_x
        target_y = football_y

    if gamemode == 'ELEMINATION':
        target_pod = (enemy_target * 3) % len(enemy_pods)
        target_x = enemy_pods[target_pod]
        target_y = enemy_pods[target_pod+1]

    # Set speed
    # check if close to goal then break
    if i == 0:
        thrust = 100

    #if i % 200 == 50 + randomness:
    #    thrust = "BOOST"
    #if i % 100 == 20 + randomness:
    #    thrust = "SHIELD"
    i = i+1
    dist_log[i] = next_checkpoint_dist
    if i > 6:
        moved = abs(dist_log[i-5]-next_checkpoint_dist)
        #print("---- moved: {}".format(moved), file=sys.stderr, flush=True)
    if i > 6 and moved < 200:
        pod_is_still = True
    else:
        pod_is_still = False

    relative_dist = next_checkpoint_dist/full_dist
    #relative_dist = full_dist-next_checkpoint_dist
    #print("---- relative_dist: {}".format(relative_dist), file=sys.stderr, flush=True)
    if second_round and goal == boost_target and ((i-boost_i > 200) or first_boost):
        thrust = "BOOST"
        boost_i = i
        first_boost = False
    if next_checkpoint_dist > 1300:
        thrust = 100
    if next_checkpoint_dist < 1300:
        thrust = 0
    if next_checkpoint_dist < 1000:
        thrust = 50
    if pod_is_still:
        thrust = 100


    cp =[next_checkpoint_x, next_checkpoint_y]
    if cp not in checkpoints:
        checkpoints.append(cp)

    guard_xy = [pod_states[3], pod_states[4]]
    guard_target = checkpoints[0]

    
    print(cp, file=sys.stderr, flush=True)
    closing_in = False
    if len(checkpoints) == 4:
        closing_in = cp == checkpoints[0]

    if closing_in:
        guard_target = [guard_target[0]-1000, guard_target[1]-1000]
    
    guard_dist = distance(guard_target, guard_xy)    
    guard_thrust = get_guard_thrust(guard_dist)
    
    if closing_in and guard_dist<400:
        guard_thrust = 'SHIELD'

    #if relative_dist > 0.5:
    #    thrust = 100
    #if relative_dist < 0.5:
    #    thrust = 50
    #if next_checkpoint_dist <relative_dist < 0.1:
    #    thrust = 10
    # if relative_dist < 0.1:
    #    thrust = 0
    # Write an action using print
    # To debug:
    #print("next_checkpoint_dist: {}".format(next_checkpoint_dist), file=sys.stderr, flush=True)
    #print("Turn: {}".format(i), file=sys.stderr, flush=True)



    # Output format for single pod matches "target_x target_y thrust"
    # Output format for dual pod matches "pod1_target_x pod1_target_y pod2_thrust - pod2_target_x pod2_target_y pod2_thrust"
    # target_x and target_y is integeres
    # Thrust is an interger value between 0 and 100

    # Replace trust with "BOOST" for a temporary speed boost. Has recharge time 200 turns.
    # Replace trust with "SHIELD" for a shield against collisions. Comes with a speed penelty for 10 turns. Has recharge time of 100 turns.

    if len(pod_states) == 6:
        # print(str(target_x) + " " + str(target_y) + " " + str(thrust) + " " + str(7000) + " " + str(7000) + " " + str(thrust), flush=True)
        print(str(target_x) + " " + str(target_y) + " " + str(thrust) + " " + str(guard_target[0]) + " " + str(guard_target[1]) + " " + str(guard_thrust), flush=True)

    else:
        print(str(target_x) + " " + str(target_y) + " " + str(thrust), flush=True)

    # Other notes:
    # - The visualisation of the arena is 16000 * 9000.
    # - Each pod has a radius of 400.
    # - Each checkpoint in races has a radius of 600.
    # - Goals in football have a radius of 1600 and is located at [0, 4500] and [16000, 4500]
    # - The ball in football can't leave the visual arena
    # - In elemination Pods needs to stay inside 1000 < x < 15000 and 1000 < y < 8000
