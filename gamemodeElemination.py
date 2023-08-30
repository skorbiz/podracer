import math
import numpy as np
from player import PlayerAdvanced
from gamemode import PlayerBase, GameModeBase
from simulator import Simulator
from visualization import LineComponent



class PlayerElemination(PlayerBase):
    def __init__(self, player, simulator, visualization, i, x, y, theta, team, is_dual_pod, boundry_x, boundry_y,is_teams):
        PlayerBase.__init__(self, player, simulator, visualization, i, x, y, theta, team, is_dual_pod, is_teams)
        self.boundry_x = boundry_x
        self.boundry_y = boundry_y
        self.enabled_pods = [1]
        if is_dual_pod:
            self.enabled_pods.append(1)
    
    def write_to_player(self, players):    
        pod_states = self.get_pod_states()

        for i,p in enumerate(pod_states):
            if self.boundry_x[0] > p[0] or p[0] > self.boundry_x[1]:
                self.enabled_pods[i] = 0
            elif self.boundry_y[0] > p[1] or p[1] > self.boundry_y[1]:
                self.enabled_pods[i] = 0

        super().write_to_player(players)

        
    def read_from_player(self, simulator_targets_velocities):    
        super().read_from_player(simulator_targets_velocities)

        for enabled_pod, sim_idx in zip(self.enabled_pods, self.sim_pod_idx):
            if enabled_pod == 0:
                simulator_targets_velocities[sim_idx] = [0, 0, 0]



class GameModeElemination(GameModeBase):
    def __init__(self, players, is_dual_pod = False, is_teams = False):
        GameModeBase.__init__(self, players, is_dual_pod, is_teams)

        boundery_max_x = 15000
        boundery_min_x = 1000
        boundery_max_y = 8000
        boundery_min_y = 1000
        # boundery_max_x = 10000
        # boundery_min_x = 5000
        # boundery_max_y = 7000
        # boundery_min_y = 3000

        line_component = LineComponent([[boundery_min_x, boundery_min_y], 
                                        [boundery_min_x, boundery_max_y], 
                                        [boundery_max_x, boundery_max_y], 
                                        [boundery_max_x, boundery_min_y]])
        self.visualization.add_component(line_component)



        for i,p in enumerate(players):
            theta = i * 2 * np.math.pi / len(players)
            x = 8000 + 2000 * math.cos(theta)
            y = 4500 + 2000 * math.sin(theta)
            team = i % 2 if is_teams else i
            number_of_pods = 2 if is_dual_pod else 1
            player_advanced = PlayerAdvanced(p, is_dual_pod, "ELEMINATION")
            player_elemination = PlayerElemination(player_advanced, self.simulator, self.visualization, i, x, y, theta, team, is_dual_pod, [boundery_min_x, boundery_max_x], [boundery_min_y, boundery_max_y], is_teams)
            self.game_players.append(player_elemination)

