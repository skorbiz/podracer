import sys
import math

# Goal chasing bot globals
last_x = 0
last_y = 0
start_dist_to_next = 0
oversteer_x = 0
oversteer_y = 0
dist_moved = 0
old_dist_to_target = 0
dit_moved_hist=5
lastBoost = 0
boost_distMoved = 0
lastShield = 0
old_enemies = list()
# Figher bot globals
enemy_distance = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
old_enemy_x = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
old_enemy_y = [0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0]
oldfx = 0
oldfy = 0

# Gamemode is either RACE, FOOTBALL, ELEMINATION
gamemode = input()
print(gamemode, file=sys.stderr, flush=True)


import random
enemy_target = random.randint(0, 10)
randomness = random.randint(0, 50)
i = 0

def getCollisionDists(enemy_pods:list, podx, pody, podtheta) -> list:
    retVal = list()

    i = 0
    while (i < (len(enemy_pods))):
        tmp = dict()
        sys.stderr.write(str(i))
        sys.stderr.write("\n")
        tmp['x'] = enemy_pods[i]
        tmp['y'] = enemy_pods[i+1]
        tmp['theta'] = enemy_pods[i+2]
        tmp['dist'] = math.sqrt((enemy_pods[i]-pody)*(enemy_pods[i]-pody)+(enemy_pods[i+1]-podx)*(enemy_pods[i+1]-podx))

        retVal.append(tmp)
        i = i+3
    return retVal

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
        for id1 in range(int(len(enemy_pods)/3)):
            old_enemy_x[id1] = enemy_pods[0+id1*3]
            old_enemy_y[id1] = enemy_pods[1+id1*3]
    for id1 in range(int(len(enemy_pods)/3)):
        dex = enemy_pods[0+id1*3] - old_enemy_x[id1]
        dey = enemy_pods[1+id1*3] - old_enemy_y[id1]
        enemy_distance[id1] = enemy_distance[id1] + math.sqrt(dex*dex + dey*dey)
    furthest_id = 0
    furthest_dist = 0
    for id1 in range(int(len(enemy_pods)/3)):
        if enemy_distance[id1] > furthest_dist:
            furthest_dist = enemy_distance[id1]
            furthest_id = id1

    if (len(pod_states) == 3):
        pod_x, pod_y, pod_theta = pod_states
    else:
        pod_x, pod_y, pod_theta, pod1_x, pod1_y, pod1_theta = pod_states
       
    thrust = 10000
    # if i % 200 == 0 and (next_checkpoint_dist > 3000):
    #     thrust = "BOOST"
    # if i % 100 == 20 + randomness:
    #     thrust = "SHIELD"
    i = i+1

    pod_to_enemies = getCollisionDists(enemy_pods, pod_x, pod_y, pod_theta)

    target_x = 5000
    target_y = 5000
    if gamemode == 'RACE':
        next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = objectives

        ##############################################
        #####  Goal chasing bot - start
        ##############################################
        # Next goal changed, capture new data
        if (last_x != next_checkpoint_x) or (last_y != next_checkpoint_y):
            sys.stderr.write("Checkpoint updated "+str(next_checkpoint_x)+" "+str(next_checkpoint_y)) 
            last_x = next_checkpoint_x
            last_y = next_checkpoint_y
            start_dist_to_next = next_checkpoint_dist


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
            sys.stderr.write("Goal brake "+str(target_x)+", "+str(target_y)+", "+str(next_checkpoint_angle)+", "+str(pod_theta)+", speed: "+str(thrust)+"\n") 
        elif next_checkpoint_dist < (start_dist_to_next/2):
            thrust = int(next_checkpoint_dist)
            sys.stderr.write("Goal search "+str(target_x)+", "+str(target_y)+", "+str(next_checkpoint_angle)+", "+str(pod_theta)+", speed: "+str(thrust)+"\n") 

        else:
            #sys.stderr.write("Oversteering"+str(oversteer_x)+" "+str(oversteer_y)) 
            target_x = next_checkpoint_x + 2*oversteer_x
            target_y = next_checkpoint_y + 2*oversteer_y
            sys.stderr.write("Drive oversteer "+str(target_x)+", "+str(target_y)+", "+str(next_checkpoint_angle)+", "+str(pod_theta)+", speed: "+str(thrust)+"\n") 

        
        ##############################################
        #####  Goal chasing bot - end
        ##############################################
        # Check if we should use boost/shield
        closest_enemy = 999999
        
        for entry in pod_to_enemies:
            if entry['dist'] < closest_enemy:
                closest_enemy = entry['dist']

        sys.stderr.write("Closest enemy at "+str(closest_enemy)+", shield time: "+str(i - lastShield)+", boost time: "+str(i - lastBoost)+"\n")
        # If enemy is too close, apply shield
        if (closest_enemy < 500) and ((i - lastShield > 100) or lastShield==0) and ((i - lastBoost > 70)) and (thrust < 1000):
            thrust = "SHIELD"
            lastShield = i
            sys.stderr.write("SHIELD")
        #If enemy is close, start slowing down in preparation for the shield
        elif (closest_enemy < 1000) and ((i - lastShield > 100) or lastShield==0) and ((i - lastBoost > 70)):
            thrust = int(closest_enemy/10)

        elif closest_enemy > 500 and (next_checkpoint_dist > (start_dist_to_next/2)) and ((i - lastBoost > 200) or lastBoost==0) and (boost_distMoved > 150):
            thrust = "BOOST"
            lastBoost = i
            sys.stderr.write("BOOST")

        # Track whether we are moving towards the goal before boosting
        boost_distMoved = old_dist_to_target - next_checkpoint_dist
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
        e_target_sx = enemy_pods[furthest_id*3 + 0] - old_enemy_x[furthest_id]
        e_target_sy = enemy_pods[furthest_id*3 + 1] - old_enemy_y[furthest_id]
        e_speed = math.sqrt(e_target_sx*e_target_sx + e_target_sy*e_target_sy)
        d_e_target_x = enemy_pods[furthest_id*3 + 0] - pod_states[3]
        d_e_target_y = enemy_pods[furthest_id*3 + 1] - pod_states[4]
        e_dist = math.sqrt(d_e_target_x*d_e_target_x + d_e_target_y*d_e_target_y) 
        
        d1x = pod_states[3] - oldfx
        d2y = pod_states[4] - oldfx
        vsecond = math.sqrt(d1x*d1x + d2y*d2y)
        e_time = e_dist*0.01#/(vsecond*0.005)
        e_target_x = int(enemy_pods[furthest_id*3 + 0] + e_target_sx*e_time)
        e_target_y = int(enemy_pods[furthest_id*3 + 1] + e_target_sy*e_time)
        e_thrust = math.sqrt(2*e_dist*2)
        print(str(target_x) + " " + str(target_y) + " " + str(thrust) + " " + str(e_target_x) + " " + str(e_target_y) + " " + str(int(e_thrust)), flush=True)

        #print(str(target_x) + " " + str(target_y) + " " + str(thrust) + " " + str(7000) + " " + str(7000) + " " + str(0), flush=True)
    else:
        print(str(target_x) + " " + str(target_y) + " " + str(thrust), flush=True)

    oldfx = pod_states[3]
    oldfy = pod_states[4]
    for id1 in range(int(len(enemy_pods)/3)):
        old_enemy_x[id1] = enemy_pods[id1*3]
        old_enemy_y[id1] = enemy_pods[1+id1*3]
 
    old_enemies = pod_to_enemies
    # Other notes:
    # - The visualisation of the arena is 16000 * 9000.
    # - Each pod has a radius of 400.
    # - Each checkpoint in races has a radius of 600.
    # - Goals in football have a radius of 1600 and is located at [0, 4500] and [16000, 4500]
    # - The ball in football can't leave the visual arena
    # - In elemination Pods needs to stay inside 1000 < x < 15000 and 1000 < y < 8000