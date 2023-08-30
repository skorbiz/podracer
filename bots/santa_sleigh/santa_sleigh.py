import sys
import math
last_x = 0
last_y = 0
start_dist_to_next = 0
oversteer_x = 0
oversteer_y = 0
dist_moved = 0
old_dist_to_target = 0
dit_moved_hist=5

# Gamemode is either RACE, FOOTBALL, ELEMINATION
gamemode = input()
print(gamemode, file=sys.stderr, flush=True)


import random
enemy_target = random.randint(0, 10)
randomness = random.randint(0, 50)
i = 0

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
    
   
    thrust = 10000
    # if i % 200 == 0 and (next_checkpoint_dist > 3000):
    #     thrust = "BOOST"
    # if i % 100 == 20 + randomness:
    #     thrust = "SHIELD"
    # i = i+1


    target_x = 5000
    target_y = 5000
    if gamemode == 'RACE':
        next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = objectives
        pod_x, pod_y, pod_theta = pod_states

        # Next goal changed, capture new data
        if (last_x != next_checkpoint_x) or (last_y != next_checkpoint_y):
            sys.stderr.write("Checkpoint updated "+str(next_checkpoint_x)+" "+str(next_checkpoint_y)) 
            last_x = next_checkpoint_x
            last_y = next_checkpoint_y
            start_dist_to_next = next_checkpoint_dist
            # Oversteer towards the middle
            # oversteer_x = next_checkpoint_x-pod_x
            # oversteer_y = next_checkpoint_y-pod_y

            # # We oversteer in the shorter dimension
            # if oversteer_x > oversteer_y:
            #     oversteer_x = 0
            #     if (oversteer_y + next_checkpoint_y - 4500) > (oversteer_y - next_checkpoint_y - 4500):

            # else:
            #     oversteer_y = 0

        target_x = next_checkpoint_x
        target_y = next_checkpoint_y
        # After 1/2 start dist to goal, start steering directly towards the goal
        if next_checkpoint_dist < (start_dist_to_next/5):
            # Wa brake if this close to goal
            thrust = -1000
            # Calculate distace moved
            dist_moved = old_dist_to_target - next_checkpoint_dist
            # If we moved less than a threshold, increase the threshold and apply positive speed
            if dist_moved < dit_moved_hist:
                thrust = 300
                dit_moved_hist = 50
            else:
                dit_moved_hist = 5
            sys.stderr.write("Goal brake "+str(target_x)+" "+str(target_y)+", speed: "+str(thrust)+"\n") 
        elif next_checkpoint_dist < (start_dist_to_next/2):
            thrust = next_checkpoint_dist
            sys.stderr.write("Goal search "+str(target_x)+" "+str(target_y)+", speed: "+str(thrust)+"\n") 
        else:
            #sys.stderr.write("Oversteering"+str(oversteer_x)+" "+str(oversteer_y)) 
            target_x = next_checkpoint_x + 2*oversteer_x
            target_y = next_checkpoint_y + 2*oversteer_y
            sys.stderr.write("Drive oversteer "+str(target_x)+" "+str(target_y)+", speed: "+str(thrust)+"\n") 


        old_dist_to_target = next_checkpoint_dist

    if gamemode == 'FOOTBALL':
        football_x, football_y = objectives
        target_x = football_x
        target_y = football_y
        
    if gamemode == 'ELEMINATION':
        target_pod = (enemy_target * 3) % len(enemy_pods)
        target_x = enemy_pods[target_pod]
        target_y = enemy_pods[target_pod+1]


    # Write an action using print
    # To debug: print("Debug messages...", file=sys.stderr, flush=True)
    print(i, file=sys.stderr, flush=True)


    # Output format for single pod matches "target_x target_y thrust"
    # Output format for dual pod matches "pod1_target_x pod1_target_y pod2_thrust pod1_target_x pod2_target_y pod2_thrust"
    # target_x and target_y is integeres
    # Thrust is an interger value between 0 and 100

    # Replace trust with "BOOST" for a temporary speed boost. Has recharge time 200 turns.
    # Replace trust with "SHIELD" for a shield against collisions. Comes with a speed penelty for 10 turns. Has recharge time of 100 turns.

    if len(pod_states) == 6:
        print(str(target_x) + " " + str(target_y) + " " + str(thrust) + " " + str(7000) + " " + str(7000) + " " + str(thrust), flush=True)
    else:
        print(str(target_x) + " " + str(target_y) + " " + str(thrust), flush=True)
 
    # Other notes:
    # - The visualisation of the arena is 16000 * 9000.
    # - Each pod has a radius of 400.
    # - Each checkpoint in races has a radius of 600.
    # - Goals in football have a radius of 1600 and is located at [0, 4500] and [16000, 4500]
    # - The ball in football can't leave the visual arena
    # - In elemination Pods needs to stay inside 1000 < x < 15000 and 1000 < y < 8000