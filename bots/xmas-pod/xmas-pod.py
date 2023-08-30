from math import atan2, degrees, radians, sqrt, tan, pow, sin, cos
import random
import sys

from numpy import rad2deg


def loop_race():
    main_pod = None
    helper_pod = None

    enemy_pods = []
    friendly_pods = []

    # game loop
    while True:
        # pod_state: [x1, y1, theta1] or [x1, y1, theta1, x2, y2, theta2]
        pod_states = IO.get_input()
        if not main_pod:
            if len(pod_states) == 6:
                helper_pod = ControllablePod("Helper")
            main_pod = ControllablePod("Main")

        main_pod.set_position(*pod_states[:3])
        if helper_pod:
            helper_pod.set_position(*pod_states[3:])

        # objectives: [next_checkpoint_x, next_checkpoint_y] for RACE, [] for ELEMINATION or [ball_x, ball_y] for FOOTBALL
        objectives = IO.get_input()

        # enemy_pods: [enemy_x1, enemy_y1, enemy_theta1, enemy_x2, enemy_y2, enemy_theta2, ...]
        enemy_pods_input = IO.get_input()
        if not enemy_pods:
            enemy_pods = [Pod("Enemy {}".format(idx))
                          for idx in range(len(enemy_pods_input)//3)]

        for idx in range(len(enemy_pods_input)//3):
            enemy_pods[idx].set_position(*enemy_pods_input[idx*3:idx*3+3])

        # friendly_pods: [friend_x1, friend_y1, friend_theta1, friend_x2, friend_y2, friend_theta2, ...]
        friendly_pods_input = IO.get_input()
        if not friendly_pods:
            friendly_pods = [Pod("Friend {}".format(idx))
                             for idx in range(len(friendly_pods_input)//3)]

        for idx in range(len(friendly_pods_input)//3):
            friendly_pods[idx].set_position(
                *friendly_pods_input[idx*3:idx*3+3])

        next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, next_checkpoint_angle = objectives
        main_pod.target_x = next_checkpoint_x
        main_pod.target_y = next_checkpoint_y

        # old logic

        next_checkpoint_angle = calc_angle_to_target(
            main_pod.pos.x, main_pod.pos.y, main_pod.pos.th, next_checkpoint_x, next_checkpoint_y)

        dist_thresh = 2500
        thrust = 100
        if next_checkpoint_dist < dist_thresh:
            thrust = int(1 + 99 * (next_checkpoint_dist / dist_thresh))

        if next_checkpoint_dist < 1000 and abs(next_checkpoint_angle) > 10:
            thrust = thrust * (1 - abs(next_checkpoint_angle) / 180)

        if abs(next_checkpoint_angle > 90):
            thrust = 10

        main_pod.thrust = thrust

        for p in enemy_pods:
            i = main_pod.check_collision(p)
            if i is not None:
                IO.debug(f"{i} {p.name} <> {main_pod.name}")
                if i < 3 and main_pod.can_shield():
                    main_pod.set_thrust("SHIELD")

        dists = []
        for p in enemy_pods:
            dists.append((helper_pod.dist(p), p))

        closest = min(dists, key=lambda x: x[0])[1]

        helper_pod.set_target(closest.pos.x, closest.pos.y, 100)
        if helper_pod.check_collision(closest) is not None:
            if helper_pod.can_boost():
                helper_pod.set_thrust('BOOST')
            elif helper_pod.can_shield():
                helper_pod.set_thrust('SHIELD')

        IO.debug(
            f"i: {Pod.gametick} - MainPod: {main_pod.pos.x} {main_pod.pos.y} {main_pod.pos.th} {main_pod.velocity} Thrust: {thrust}")

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)
        # print(next_checkpoint_dist, thrust,
        #       int(next_checkpoint_angle), current_vel, file=sys.stderr, flush=True)

        # Output format for single pod matches "target_x target_y thrust"
        # Output format for dual pod matches "pod1_target_x pod1_target_y pod2_thrust pod1_target_x pod2_target_y pod2_thrust"
        # target_x and target_y is integeres
        # Thrust is an interger value between 0 and 100

        # Replace trust with "BOOST" for a temporary speed boost. Has recharge time 200 turns.
        # Replace trust with "SHIELD" for a shield against collisions. Comes with a speed penelty for 10 turns. Has recharge time of 100 turns.

        if helper_pod:
            IO.send_cmd(main_pod.target_x, main_pod.target_y, main_pod.thrust,
                        helper_pod.target_x, helper_pod.target_y, helper_pod.thrust)
        else:
            IO.send_cmd(main_pod.target_x, main_pod.target_y, main_pod.thrust)

        Pod.gametick += 1

        # Other notes:
        # - The visualisation of the arena is 16000 * 9000.
        # - Each pod has a radius of 400.
        # - Each checkpoint in races has a radius of 600.
        # - Goals in football have a radius of 1600 and is located at [0, 4500] and [16000, 4500]
        # - The ball in football can't leave the visual arena
        # - In elemination Pods needs to stay inside 1000 < x < 15000 and 1000 < y < 8000


class IO(object):
    @staticmethod
    def debug(*args, **kwargs):
        print(*args, **kwargs, file=sys.stderr, flush=True)

    @staticmethod
    def send_cmd(*args):
        send = []
        for a in args:
            try:
                a = int(a)
            except:
                pass
            send.append(str(a))
        print(" ".join(send), file=sys.stdout, flush=True)

    @staticmethod
    def get_input(as_list_of_numbers=True):
        ret = input()
        if as_list_of_numbers:
            ret = [int(i) for i in ret.split()]

        return ret


def calc_angle_to_target(pod_x, pod_y, pod_z, goal_x, goal_y):
    dx = goal_x - pod_x
    dy = goal_y - pod_y
    a = atan2(dy, dx)
    a = degrees(a)
    angle = (pod_z - a)
    while angle > 180:
        angle = angle - 180
    while angle < -180:
        angle = angle + 180
    return angle


class Pos2D(object):
    def __init__(self, x=0, y=0, th=0):
        self.x = x
        self.y = y
        self.th = th

    def copy(self):
        return self.__class__(self.x, self.y, self.th)


class Pod(object):
    gametick = 0

    def __init__(self, name):
        self.name = name
        self.pos = Pos2D()
        self.last_pos = None

        self.dx = 0
        self.dy = 0
        self.velocity = 0

    def set_position(self, x, y, th):
        self.pos.x = x
        self.pos.y = y
        self.pos.th = th

        if self.last_pos:
            self.dx = self.pos.x - self.last_pos.x
            self.dy = self.pos.y - self.last_pos.y
            self.velocity = int(sqrt(self.dx * self.dx + self.dy * self.dy))

        self.last_pos = self.pos.copy()

    def get_future_pose(self, iterations=1):
        next_pose = self.pos.copy()
        next_pose.x = next_pose.x + self.dx * iterations
        next_pose.y = next_pose.y + self.dy * iterations
        return next_pose

    def dist(self, other_pod):
        d_x = self.pos.x - other_pod.pos.x
        d_y = self.pos.y - other_pod.pos.y
        return sqrt(d_x * d_x + d_y * d_y)

    def is_collision(self, pos, other_pos):
        thresh = 850
        d_x = pos.x - other_pos.x
        d_y = pos.y - other_pos.y
        return sqrt(d_x * d_x + d_y * d_y) < thresh

    def check_collision(self, other_pod, iterations=10):
        for i in range(iterations):
            p1 = self.get_future_pose(i)
            p2 = other_pod.get_future_pose(i)
            if self.is_collision(p1, p2):
                return i
        return None


class ControllablePod(Pod):
    def __init__(self, name):
        super().__init__(name)
        self.target_x = 0
        self.target_y = 0
        self.thrust = 0

        self._last_boost = None
        self._last_shield = None

    def set_target(self, x, y, thrust=None):
        self.target_x = x
        self.target_y = y
        if thrust is not None:
            self.set_thrust(thrust)

    def set_thrust(self, thrust):
        if thrust == 'SHIELD':
            IO.debug(f"{self.name}: SHIELD!")
            self._last_shield = Pod.gametick
        elif thrust == 'BOOST':
            IO.debug(f"{self.name}: BOOST!")
            self._last_boost = Pod.gametick
        self.thrust = thrust

    def can_boost(self):
        if self._last_boost is None:
            return True
        return Pod.gametick - self._last_boost > 201

    def can_shield(self):
        if self._last_shield is None:
            return True
        return Pod.gametick - self._last_shield > 101

    def is_shielding(self):
        if self._last_shield is None:
            return False
        return Pod.gametick - self._last_shield < 10


def loop_football():
    main_pod = None

    enemy_pods = []
    friendly_pods = []

    our_goal = Pos2D(0, 4500, 0)
    their_goal = Pos2D(16000, 4500, 0)

    # game loop
    while True:
        # pod_state: [x1, y1, theta1] or [x1, y1, theta1, x2, y2, theta2]
        pod_states = IO.get_input()
        if not main_pod:
            main_pod = ControllablePod("Main")

        main_pod.set_position(*pod_states[:3])

        if Pod.gametick == 0:
            if main_pod.pos.x > 8000:
                their_goal, our_goal = our_goal, their_goal

        # objectives: [next_checkpoint_x, next_checkpoint_y] for RACE, [] for ELEMINATION or [ball_x, ball_y] for FOOTBALL
        objectives = IO.get_input()

        # enemy_pods: [enemy_x1, enemy_y1, enemy_theta1, enemy_x2, enemy_y2, enemy_theta2, ...]
        enemy_pods_input = IO.get_input()
        if not enemy_pods:
            enemy_pods = [Pod("Enemy {}".format(idx))
                          for idx in range(len(enemy_pods_input)//3)]

        for idx in range(len(enemy_pods_input)//3):
            enemy_pods[idx].set_position(*enemy_pods_input[idx*3:idx*3+3])

        # friendly_pods: [friend_x1, friend_y1, friend_theta1, friend_x2, friend_y2, friend_theta2, ...]
        friendly_pods_input = IO.get_input()
        if not friendly_pods:
            friendly_pods = [Pod("Friend {}".format(idx))
                             for idx in range(len(friendly_pods_input)//3)]

        for idx in range(len(friendly_pods_input)//3):
            friendly_pods[idx].set_position(
                *friendly_pods_input[idx*3:idx*3+3])

        next_checkpoint_x, next_checkpoint_y = objectives
        next_checkpoint_dist = sqrt(pow(
            main_pod.pos.x - next_checkpoint_x, 2.0) + pow(main_pod.pos.y - next_checkpoint_y, 2.0))

        # old logic
        goal_ball_angle = - \
            calc_angle_to_target(
                next_checkpoint_x, next_checkpoint_y, 0, their_goal.x, their_goal.y)

        next_checkpoint_angle = calc_angle_to_target(
            main_pod.pos.x, main_pod.pos.y, main_pod.pos.th, next_checkpoint_x, next_checkpoint_y)

        next_checkpoint_x = next_checkpoint_x - \
            1000 * cos(radians(goal_ball_angle))
        next_checkpoint_y = next_checkpoint_y - \
            1000 * sin(radians(goal_ball_angle))
        next_checkpoint_dist = sqrt(pow(
            main_pod.pos.x - next_checkpoint_x, 2.0) + pow(main_pod.pos.y - next_checkpoint_y, 2.0))

        main_pod.target_x = next_checkpoint_x - \
            min(2000, max(0, next_checkpoint_dist - 1000)) * \
            cos(radians(goal_ball_angle))
        main_pod.target_y = next_checkpoint_y - \
            min(2000, max(0, next_checkpoint_dist - 1000)) * \
            sin(radians(goal_ball_angle))

        dist_thresh = 1500
        thrust = 100
        if next_checkpoint_dist < dist_thresh:
            thrust = int(30 + 70 * (next_checkpoint_dist / dist_thresh))

        if next_checkpoint_dist < 800:
            thrust = int(100 - 70 * (next_checkpoint_dist / 800))

        if Pod.gametick == 4:
            thrust = 'BOOST'

        if Pod.gametick == 5:
            thrust = 'SHIELD'

        if Pod.gametick > 12 and main_pod.can_boost():
            thrust = 'BOOST'

        main_pod.set_thrust(thrust)

        # for p in enemy_pods:
        #     i = main_pod.check_collision(p)
        #     if i is not None:
        #         IO.debug(f"{i} {p.name} <> {main_pod.name}")
        #         if i < 3 and main_pod.can_shield():
        #             main_pod.set_thrust("SHIELD")

        IO.debug(f"i: {Pod.gametick} {goal_ball_angle:.2f} {next_checkpoint_angle:.2f} - MainPod: {main_pod.pos.x} {main_pod.pos.y} {main_pod.pos.th} {main_pod.velocity} Thrust: {thrust}")

        # Write an action using print
        # To debug: print("Debug messages...", file=sys.stderr, flush=True)
        # print(next_checkpoint_dist, thrust,
        #       int(next_checkpoint_angle), current_vel, file=sys.stderr, flush=True)

        # Output format for single pod matches "target_x target_y thrust"
        # Output format for dual pod matches "pod1_target_x pod1_target_y pod2_thrust pod1_target_x pod2_target_y pod2_thrust"
        # target_x and target_y is integeres
        # Thrust is an interger value between 0 and 100

        # Replace trust with "BOOST" for a temporary speed boost. Has recharge time 200 turns.
        # Replace trust with "SHIELD" for a shield against collisions. Comes with a speed penelty for 10 turns. Has recharge time of 100 turns.

        IO.send_cmd(main_pod.target_x, main_pod.target_y, main_pod.thrust)

        Pod.gametick += 1

        # Other notes:
        # - The visualisation of the arena is 16000 * 9000.
        # - Each pod has a radius of 400.
        # - Each checkpoint in races has a radius of 600.
        # - Goals in football have a radius of 1600 and is located at [0, 4500] and [16000, 4500]
        # - The ball in football can't leave the visual arena
        # - In elemination Pods needs to stay inside 1000 < x < 15000 and 1000 < y < 8000


class GameMode(object):
    RACE = 1
    FOOTBALL = 2
    ELIMINATION = 3


def loop(gamemode):
    if gamemode == GameMode.RACE:
        loop_race()
    elif gamemode == GameMode.FOOTBALL:
        loop_football()


def get_gamemode():
    # Gamemode is either RACE, FOOTBALL, ELEMINATION
    gamemode_str = IO.get_input(False)
    if gamemode_str == 'RACE':
        return GameMode.RACE
    elif gamemode_str == 'FOOTBALL':
        return GameMode.FOOTBALL
    elif gamemode_str == 'ELEMINATION':
        return GameMode.ELIMINATION


def main():
    gamemode = get_gamemode()

    loop(gamemode)


if __name__ == '__main__':
    main()
