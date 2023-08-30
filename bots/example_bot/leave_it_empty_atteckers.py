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

def where_is_the_opponent_goal(pod_x):
    if pod_x <= 8000:
        opponent_goal_right = True
    else:
        opponent_goal_right = False
    return opponent_goal_right


def get_area(opponent_goal_right, attack_area_top):
    if opponent_goal_right:
        if attack_area_top:
            return 8000, 16000, 4500, 9000
        else:
            return 8000, 16000, 0, 4500
    else:
        if attack_area_top:
            return 0, 8000, 4500, 9000
        else:
            return 0, 8000, 0, 4500

def is_ball_in_attacking_area(ball_x, ball_y, opponent_goal_right, attack_area_top):
    x_min, x_max, y_min, y_max = get_area(opponent_goal_right, attack_area_top)
    return (x_min <= ball_x and ball_x <= x_max) and (y_min <= ball_y and ball_y <= y_max)


    


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
# attack_area_top = False # change for the other player

def player_action(football_x, football_y, opponent_goal_right, attack_area_top):
    if is_ball_in_attacking_area(football_x, football_y, opponent_goal_right, attack_area_top):
        target_x = football_x
        target_y = football_y
        thrust = 100

    else:
        target_x = 8000
        if attack_area_top:
            target_y = 7000
        else:
            target_y = 2000
        thrust = 30

    return target_x, target_y, thrust




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


    print(pod_states, file=sys.stderr, flush=True)



    football_x, football_y = objectives
    target_x = football_x
    target_y = football_y
    if i == 0:
        opponent_goal_right = where_is_the_opponent_goal(pod_states[0])


    top_player_action = player_action(football_x, football_y, opponent_goal_right, True)
    bottom_player_action = player_action(football_x, football_y, opponent_goal_right, False)
    


   


    # Output format for single pod matches "target_x target_y thrust"
    # Output format for dual pod matches "pod1_target_x pod1_target_y pod2_thrust - pod2_target_x pod2_target_y pod2_thrust"
    # target_x and target_y is integeres
    # Thrust is an interger value between 0 and 100

    # Replace trust with "BOOST" for a temporary speed boost. Has recharge time 200 turns.
    # Replace trust with "SHIELD" for a shield against collisions. Comes with a speed penelty for 10 turns. Has recharge time of 100 turns.

    if len(pod_states) == 6:
        print(str(top_player_action[0]) + " " + str(top_player_action[1]) + " " + str(top_player_action[2]) + " " + str(bottom_player_action[0]) + " " + str(bottom_player_action[1]) + " " + str(bottom_player_action[2]), flush=True)
        # print(str(target_x) + " " + str(target_y) + " " + str(thrust) + " " + str(guard_target[0]) + " " + str(guard_target[1]) + " " + str(guard_thrust), flush=True)

    else:
        print(str(target_x) + " " + str(target_y) + " " + str(thrust), flush=True)

    # Other notes:
    # - The visualisation of the arena is 16000 * 9000.
    # - Each pod has a radius of 400.
    # - Each checkpoint in races has a radius of 600.
    # - Goals in football have a radius of 1600 and is located at [0, 4500] and [16000, 4500]
    # - The ball in football can't leave the visual arena
    # - In elemination Pods needs to stay inside 1000 < x < 15000 and 1000 < y < 8000
