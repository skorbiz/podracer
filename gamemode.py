import math
import numpy as np
from player import PlayerAdvanced
from simulator import Simulator
from visualization import Visualization, UfoComponent
import time



class PlayerBase(object):
    
    def __init__(self, player, simulator, visualization, i, x, y, theta, team, is_dual_pod, is_team):
        isinstance(player, PlayerAdvanced)
        self.player = player
        self.simulator = simulator
        self.visualization = visualization
        self.team = team
        self.is_dual_pod = is_dual_pod
        self.identifier = i
        self.sim_pod_idx = []

        i = self.simulator.add_ufo([x,y], theta)
        callback = lambda: self.simulator.get_ufo_state(i)
        ufo_component = UfoComponent(self.identifier, [x,y], 400, callback, is_team)
        self.visualization.add_component(ufo_component)
        self.sim_pod_idx.append(i)

        if self.is_dual_pod:
            x,y,theta = self.starting_position_second_pod(x,y,theta)
            j = self.simulator.add_ufo([x,y], theta) 
            # ToDo this is probably subject to the mercy of the garbage collector
            callback = lambda: self.simulator.get_ufo_state(j)
            ufo_component = UfoComponent(self.identifier, [x,y], 400, callback, is_team)
            self.visualization.add_component(ufo_component)
            self.sim_pod_idx.append(j)
    
    def get_pod_states(self):
        pod_states = []
        for i in self.sim_pod_idx:
            pos,angle, shield = self.simulator.get_ufo_state(i)
            pod_states.append([pos[0], pos[1], angle])
        return pod_states

    def write_to_player(self, players):    
        pod_states = self.get_pod_states()
        objectives = self.get_objectives(pod_states)
        enemy_pods = []
        friendly_pods = []

        for p in players:
            if p.identifier == self.identifier:
                continue
            elif p.team == self.team:
                friendly_pods.extend(p.get_pod_states())
            else:
                enemy_pods.extend(p.get_pod_states())
        self.player.write_to_player(pod_states, objectives, enemy_pods, friendly_pods)
        
    def read_from_player(self, simulator_targets_velocities):   
        actions = self.player.read_from_player()
        for i, sim_idx in enumerate(self.sim_pod_idx):
            simulator_targets_velocities[sim_idx] = actions[i]
    

    def starting_position_second_pod(self, pod1_x, pod1_y, pod1_theta, distance = 1000):
        pod2_x = pod1_x + math.cos(pod1_theta + math.pi) * distance
        pod2_y = pod1_y + math.sin(pod1_theta + math.pi) * distance
        return pod2_x, pod2_y, pod1_theta

    def get_objectives(self, pod_states):
        return []
    
class GameModeBase:

    def __init__(self, players, is_dual_pod = False, is_teams = False):

        self.time = 0
        self.visualization = Visualization(self.update, players, is_teams)
        self.simulator = Simulator()

        self.is_dual_pod = is_dual_pod
        
        self.game_players = []
        self.TARGET_UPDATE_TIME = 0.1

        self.temp = 0
        self.time_start = time.time()
        self.time_end = time.time()
    
    def update_child(self):
        pass

    # def update(self):
    #     self.update(0.0002)
    
    def update(self):

        #delta_time = 0.1
        delta_time = time.time() - self.time_start
        self.time_start = time.time()
        self.step(delta_time)
        # self.step(0.1)


        #print("Player time scine last update: {:0.2f}ms".format((time.time() - self.time_end)*1000))
        self.time_end = time.time()
        #print("Player update time: {:0.2f}ms".format((self.time_end - self.time_start)*1000))
        #print(self.temp)
        self.temp = 0


    def update_fixed_time(self, delta_time):
        self.step(delta_time)


    def step(self, delta_time):
        self.simulator.step_simulation(delta_time)
        self.time += delta_time

        #print("Time {:0.2f}ms and delta_time {:0.2f}ms ".format(self.time *1000, delta_time*1000))
        if self.time < self.TARGET_UPDATE_TIME:
            return

        self.time -= self.TARGET_UPDATE_TIME

        number_of_pods = len(self.game_players)
        if self.is_dual_pod:
            number_of_pods *= 2

        for p in self.game_players:
            p.write_to_player(self.game_players)

        simulator_targets_velocities = [[0,0,0]] * number_of_pods
        for p in self.game_players:
            p.read_from_player(simulator_targets_velocities)

        simulator_targets_velocities_transposed = list(zip(*simulator_targets_velocities))
        target_x_list = simulator_targets_velocities_transposed[0]
        target_y_list = simulator_targets_velocities_transposed[1]
        target_thrust_list = simulator_targets_velocities_transposed[2]

        self.simulator.update_targets(target_x_list, target_y_list, target_thrust_list)
        self.update_child()


         
    def run(self):
        #print("Run")
        self.visualization.run()

    def run_without_vizualization(self):
        for i in range(2000):
            self.update_fixed_time(0.1)

            if self.visualization.winner is not None:
                print("Winner is: {}".format(self.visualization.winner))
                return
       
        print("Draw")
