
#!/usr/bin/python
import sys
import os
import subprocess
import numpy

# https://stackoverflow.com/questions/33313566/python-subprocess-multiple-stdin-write-and-stdout-read

class PlayerAdvanced:
    
    def __init__(self, player, two_pods=False, init_line=None):
        isinstance(player, Player)
        self.player = player
        self.two_pods = two_pods

        if init_line is not None:
            self.player.write_to_player(init_line)

    def write_to_player(self, pod_states, objectives, ennemy_pods = [], friendly_pods = []):
        self.player.write_to_player(self.parse_pod_states(pod_states))
        self.player.write_to_player(self.parse_objective_state(objectives))
        self.player.write_to_player(self.parse_pod_states(ennemy_pods))
        self.player.write_to_player(self.parse_pod_states(friendly_pods))

    def read_from_player(self):
        player_action = self.player.read_from_player()
        return self.parse_player_action(player_action)

    def parse_pod_states(self, states):
        return " ".join([self.parse_pod_state(p) for p in states])

    def parse_pod_state(self, state):
        angle = numpy.rad2deg(state[2])
        return "{:.0f} {:.0f} {:.0f}".format(state[0], state[1], angle)

    def parse_objective_state(self, objective_state):
        state_int = list(map(int, objective_state))
        state_str = list(map(str, state_int))
        return " ".join(state_str)

    def parse_player_action(self, player_action):
        try:
            actions_str = player_action.split()
            if(self.two_pods):
                return [self.validate_pod_action(actions_str[0:3]), 
                        self.validate_pod_action(actions_str[3:6])]
            return [self.validate_pod_action(actions_str[0:3])]
        except:
            print("Not able to pass player_action for {} got: {}".format(self.player.name, player_action))
            if(self.two_pods):
                return [[0,0,0],[0,0,0]]
            return [[0,0,0]]


    def validate_pod_action(self,actions_str):
        try:
            target_x = self.validate_target(actions_str[0])
            target_y = self.validate_target(actions_str[1])
            target_thrust = self.validate_thrust(actions_str[2])
            return [target_x, target_y, target_thrust]
        except:
            print("Not able to pass player_action for {} got: {}".format(self.player.name, actions_str))
            return [0, 0, 0]

        

    def validate_target(self, target):
        try:
            return int(target)
        except ValueError as verr:
            print("Failed to decode target value: {}".format(target))
            return 0
    
    def validate_thrust(self, thrust):
        if any(thrust.upper() == k for k in ["BOOST", "SHIELD"]):
            return thrust.upper()
        try:
            output = int(thrust)
            return min(max(output, 0), 100)
        except ValueError as verr:
            print("Failed to decode thrust value: {}".format(thrust))
            return 0
            
class Player:
    
    def __init__(self, path, debug_print = False):
        self.name = os.path.basename(path)
        if path.endswith(".py"):
            self.process = subprocess.Popen([sys.executable, '-u', path], stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)
        else:    
            self.process = subprocess.Popen(path, stdin=subprocess.PIPE, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True, bufsize=1)    
        self.debug_print = debug_print

    def update(self, input):
        self.write_to_player(input)
        return self.read_from_player()

    def write_to_player(self, input):
        try:
            print(input, file=self.process.stdin, flush=True)
            # if(self.debug_print):
            #     print("player_state:", input)
        except:
            print("An exception occurred when writing player state")

    def read_from_player(self):
        try:
            output = self.process.stdout.readline()
            if(self.debug_print):
                print("player_action:", output, end="")
            return output
        except:
            print("An exception occurred when reading player action")
            return "ERROR"


    def terminate(self):
        self.process.terminate()

        if(self.debug_print):
            print("***** Debug print *****")
            for l in self.process.stderr.readlines():
                print(l, end='',  file=sys.stderr)
            print("***********************")
