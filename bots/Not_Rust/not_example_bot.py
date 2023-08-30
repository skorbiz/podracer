from math import sqrt
import sys
import traceback

# Gamemode is either RACE, FOOTBALL, ELEMINATION
gamemode = input()
print(gamemode, file=sys.stderr, flush=True)


import random
enemy_target = random.randint(0, 10)
randomness = random.randint(0, 50)
i = 0


goals=[]
prev_state = [0,0,0,0,0,0]


def debug(str):
    print("Debug: {}".format(str), file=sys.stderr, flush=True)

def dist(dx,dy):
    return sqrt(dx*dx+dy*dy)

class PodTracker:
    i_boost=200
    i_shield=100
    def addTurn(self):
        self.i_boost+=1
        self.i_shield+=1
    
    def isBoostAvailable(self):
        return self.i_boost >= 200
    def isShieldAvailable(self):
        return self.i_shield >= 100

    def triggerBoost(self):
        self.i_boost =0

    def triggerShield(self):
        self.i_shield =0
    def wasLastTurnBoost(self):
        return self.i_boost < 10


def closestEnemy(enemy_pods, x,y):
    number_of_enemy = int(len(enemy_pods)/3)
    cloest_dist = 10000000000
    closest_enemy = (0,0,0)
    for i in range(number_of_enemy):
        dist_meas = dist(x-enemy_pods[i*3+0], y- enemy_pods[i*3+1])

        if dist_meas < cloest_dist:
            cloest_dist = dist_meas
            closest_enemy = (enemy_pods[i*3+0],enemy_pods[i*3+1],enemy_pods[i*3+2])
    
    return closest_enemy


def getRaceTarget(objectives, pod_states, prev_state,race_pod,block_pod, enemy_pods):
    x = 0
    y = 0
    thrust = 100

    bx=14000
    by=2000
    bthrust=70



    next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = objectives

    x1 =None
    y1 =None
    theta1=None
    x2=None
    y2=None
    theta2=None

    prev_x1 = prev_state[0]
    prev_y1 = prev_state[1]
    prev_heta1= prev_state[2]
    if(len(prev_state)>3):
        prev_x2= prev_state[3]
        prev_y2= prev_state[4]
        prev_heta2= prev_state[5]

    if(len(pod_states)==3):
        x1,y1,theta1 = pod_states
    else:
        x1,y1,theta1,x2,y2,theta2 = pod_states


    goal_dist = dist(bx-prev_x2, by-prev_y2)

    closest_enemy = closestEnemy(enemy_pods,x2,y2)

    if(goal_dist < 3000):
        bx=closest_enemy[0]
        by=closest_enemy[1]
        bthrust = 100

        dist_to_enemy = dist(closest_enemy[0]-prev_x2, closest_enemy[1]-prev_y2)
        if(abs(prev_heta2) < 10 and dist_to_enemy < 1500):
            if (block_pod.isBoostAvailable()):
                bthrust = "BOOST"
                block_pod.triggerBoost()
        if not block_pod.isBoostAvailable() and block_pod.isShieldAvailable() and  dist_to_enemy < 1000:
            bthrust = "SHIELD"
            block_pod.triggerShield()
    # debug("Target dist: {} angle: {}".format(next_checkpoint_dist,next_checkpoint_angle))


    dx = next_checkpoint_x -x1
    dy =  next_checkpoint_y - y1

    odom_x = x1 - prev_x1
    odom_y = y1 - prev_y1

    vel = dist(odom_x,odom_y)

    perp_goal_x = -dy
    prep_goal_y = dx

    length = dist(perp_goal_x,prep_goal_y)

    perp_goal_x /= length
    prep_goal_y /= length


    #ax × bx + ay × by

    drift = abs( odom_x * perp_goal_x + odom_y * prep_goal_y) 
    #drift = odom_x * dx + odom_y * dy

    debug("Odom_x: {} Odom_y: {}".format(odom_x,odom_y))
    debug("Drift: {}".format(drift))

    slow_thrust = 80
    medium_thrust = 90

    # if drift > 100:
    if drift > 200:
        thrust = slow_thrust
    elif drift > 100:
        thrust = medium_thrust

    

    if  (next_checkpoint_dist < 500 and next_checkpoint_dist > 150) and vel > 250 :
        thrust= slow_thrust


    if (drift< 10 and race_pod.isBoostAvailable() and next_checkpoint_dist>1500 and vel > 200):
        thrust = "BOOST"
        race_pod.triggerBoost()


    try:

        closest_enemy_1 = closestEnemy(enemy_pods,x1,y1)
        dist_to_enemy_1 = dist(closest_enemy_1[0]-x1, closest_enemy_1[1]-y1)


        # if not race_pod.isBoostAvailable() and race_pod.isShieldAvailable() and  closest_enemy_1 < 1500 and vel > 200:
        if not race_pod.isBoostAvailable() and race_pod.isShieldAvailable() and vel > 200 and i > 60 and  dist_to_enemy_1 < 1500:
                thrust = "SHIELD"
                race_pod.triggerShield()
                
    except:
        traceback.print_exc()
    # if (race_pod.wasLastTurnBoost() and race_pod.isShieldAvailable()):
    #     thrust = "SHIELD"
    #     race_pod.triggerShield()



    x = int(x1 + dx)
    y = int(y1 + dy)

    debug("next_checkpoint_x: {} next_checkpoint_y: {}".format(next_checkpoint_x,next_checkpoint_y))
    debug("x: {} y: {}".format(x,y))

    return (x,y, thrust, bx, by, bthrust)

race_pod = PodTracker()
block_pod = PodTracker()
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
    


    goal = (objectives[0],objectives[1])
    if goal not in goals:
        goals.append(goal)

    debug("Goals: {}".format(goals))

    

    thrust = 100
    # if i % 200 == 50 + randomness:
    #     thrust = "BOOST"
    # if i % 100 == 20 + randomness:
    #     thrust = "SHIELD"
    # i = i+1


    target_a_x = 5000
    target_a_y = 5000
    thrust_a=100
    target_b_x = 5000
    target_b_y = 5000
    thrust_b = 100
    if gamemode == 'RACE':
        next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = objectives
        
        target_a_x, target_a_y, thrust_a, target_b_x, target_b_y, thrust_b =  getRaceTarget(objectives, pod_states,prev_state,race_pod,block_pod,enemy_pods)

    if gamemode == 'FOOTBALL':
        football_x, football_y = objectives
        target_x = football_x
        target_y = football_y
        
    if gamemode == 'ELEMINATION':
        target_pod = (enemy_target * 3) % len(enemy_pods)
        target_x = enemy_pods[target_pod]
        target_y = enemy_pods[target_pod+1]

    i+=1
    prev_state =pod_states

    race_pod.addTurn()
    block_pod.addTurn()

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
        print(str(target_a_x) + " " + str(target_a_y) + " " + str(thrust_a) + " " + str(target_b_x) + " " + str(target_b_y) + " " + str(thrust_b), flush=True)
    else:
        print(str(target_x) + " " + str(target_y) + " " + str(thrust), flush=True)
 
    # Other notes:
    # - The visualisation of the arena is 16000 * 9000.
    # - Each pod has a radius of 400.
    # - Each checkpoint in races has a radius of 600.
    # - Goals in football have a radius of 1600 and is located at [0, 4500] and [16000, 4500]
    # - The ball in football can't leave the visual arena
    # - In elemination Pods needs to stay inside 1000 < x < 15000 and 1000 < y < 8000