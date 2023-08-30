import math
import numpy as np
from player import PlayerAdvanced
from gamemode import PlayerBase, GameModeBase
from visualization import FootballComponent, CheckpointComponent


    
class PlayerFootball(PlayerBase):
    def __init__(self, player, simulator, visualization, i, x, y, theta, team, is_dual_pod, is_teams):
        PlayerBase.__init__(self, player, simulator, visualization, i, x, y, theta, team, is_dual_pod, is_teams)

    def get_objectives(self, pod_states):
        return self.simulator.get_football_state()

class GameModeFootball(GameModeBase):
    def __init__(self, players, is_dual_pod = False, is_teams = True):
        is_teams = True
        GameModeBase.__init__(self, players, is_dual_pod, is_teams)

        

        self.goal_team_1 = [0,4500]
        self.goal_team_2 = [16000,4500]
        self.goal_radius = 1600

        goal_team_1 = CheckpointComponent(self.goal_team_1, self.goal_radius)
        goal_team_2 = CheckpointComponent(self.goal_team_2, self.goal_radius)
        self.visualization.add_component(goal_team_1)
        self.visualization.add_component(goal_team_2)


        for i,p in enumerate(players):
            team = i % 2 if is_teams else i

            theta = 0
            x = 1500
            y = 4500 - 200 * len(players) + 400*i
            
            if team == 1:
                theta += math.pi
                x = 16000 -x

            player_advanced = PlayerAdvanced(p, is_dual_pod, "FOOTBALL")
            player_elemination = PlayerFootball(player_advanced, self.simulator, self.visualization, i, x, y, theta, team, is_dual_pod, is_teams)
            self.game_players.append(player_elemination)

        self.simulator.add_football([8000,4500])
        callback = lambda: self.simulator.get_football_state()
        football_component = FootballComponent([9000, 4500], 800, callback)
        self.visualization.add_component(football_component)


    def update_child(self):
        ball = self.simulator.get_football_state()
        
        if self.is_goal(ball, self.goal_team_1, self.goal_radius):
            self.visualization.set_winner("TEAM 2")
        if self.is_goal(ball, self.goal_team_2, self.goal_radius):
            self.visualization.set_winner("TEAM 1")
        

    def is_goal(self, ball, goal, goal_radius):
        #https://stackoverflow.com/questions/481144/equation-for-testing-if-a-point-is-inside-a-circle
        # (x - center_x)² + (y - center_y)² < radius²
        return (ball[0] - goal[0])**2 + (ball[1] - goal[1])**2 < goal_radius**2
            



