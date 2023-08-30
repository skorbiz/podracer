import math
import numpy as np
from player import PlayerAdvanced
from gamemode import PlayerBase, GameModeBase
from visualization import CheckpointComponent

class PlayerRace(PlayerBase):
    def __init__(self, player, simulator, visualization, i, x, y, theta, team, is_dual_pod, checkpoints, checkpoint_radius, is_teams):
        PlayerBase.__init__(self, player, simulator, visualization, i, x, y, theta, team, is_dual_pod, is_teams)

        self.lap = 0
        self.checkpoints = checkpoints
        self.checkpoint_radius = checkpoint_radius
        self.checkpoint_target_idx = 0

    def get_objectives(self, pod_states):
        x,y,theta = pod_states[0]
        if self.has_reached_checkpoint(x,y):
            self.checkpoint_target_idx = self.checkpoint_target_idx + 1

        if self.checkpoint_target_idx >= len(self.checkpoints):
            self.lap += 1
            self.checkpoint_target_idx = 0

        if self.lap == 2:
            self.visualization.set_winner(self.player.player.name)

        next_checkpoint = self.checkpoints[self.checkpoint_target_idx]
        next_checkpoint_x = next_checkpoint[0]
        next_checkpoint_y = next_checkpoint[1]
        next_checkpoint_dist = math.sqrt((x - next_checkpoint_x)**2 + (y - next_checkpoint_y)**2) 
        next_checkpoint_angle = math.atan2(y - next_checkpoint_y, x - next_checkpoint_x) #TODO This should probably be based on the pods facing angle actually

        return [next_checkpoint_x, next_checkpoint_y, next_checkpoint_dist, np.rad2deg(next_checkpoint_angle)]
    

    def has_reached_checkpoint(self, x, y):
        #https://stackoverflow.com/questions/481144/equation-for-testing-if-a-point-is-inside-a-circle
        # (x - center_x)² + (y - center_y)² < radius²
        checkpoint_x = self.checkpoints[self.checkpoint_target_idx][0]
        checkpoint_y = self.checkpoints[self.checkpoint_target_idx][1]
        return (x - checkpoint_x)**2 + (y - checkpoint_y)**2 < self.checkpoint_radius**2


class GameModeRace(GameModeBase):
    def __init__(self, players, is_dual_pod = False, is_teams = False, map = "map1"):
        GameModeBase.__init__(self, players, is_dual_pod, is_teams)
        
        maps = {
            "map1":[[4000, 7000], [14000, 7000], [14000, 2000], [4000, 2000]],
            "map2":[[4000, 7000], [14000, 7000], [2000, 2000], [14000, 2000]],
            "competion1":[[2000, 2000], [14000, 7000], [2000, 3500], [3500, 2000]]
        }
        
        import random
        maps["random1"] = [[random.randint(1000, 15000), random.randint(1000, 8000)] for i in range(4)]
        maps["random2"] = maps["map1"].copy()
        random.shuffle(maps["random1"])

        if map not in maps.keys():
            print("map did not exists")
            map = "map1"

        checkpoints = maps[map]
        checkpoint_radius = 600
        
        for cp in checkpoints:
            cp_component = CheckpointComponent(cp, checkpoint_radius)
            self.visualization.add_component(cp_component)
        
        '''
        first_checkpoint = np.array ((checkpoints[0][0], checkpoints[0][1]))
        second_checkpoint = np.array ((checkpoints[1][0], checkpoints[1][1]))
        start_vector = first_checkpoint- second_checkpoint
        print("start_vector", start_vector)

        length_behind_first_checkpoint = 1500
        start_vector = start_vector * length_behind_first_checkpoint / np.linalg.norm(start_vector) 
        print("start_vector", start_vector)

        
        for i,p in enumerate(players):
            #if i % 2 : 
            angle = np.deg2rad(20)*(i)
            x = first_checkpoint[0] + start_vector[0]*np.cos(angle) - start_vector[1]*np.sin(angle)
            y = first_checkpoint[1] + start_vector[0]*np.sin(angle) + start_vector[1] * np.cos(angle)
            
            direction_vector = first_checkpoint - np.array((x,y))
            x_axsis = np.array((1,0))
            dot_product = np.dot(direction_vector/ np.linalg.norm(direction_vector), x_axsis)  
                theta = np.arccos(dot_product)    
            theta = i * 2 * np.math.pi / len(players)
            '''
        cp1 = np.array(checkpoints[0])
        cp2 = np.array(checkpoints[1])
        angle = math.atan2(cp2[1]-cp1[1], cp2[0]-cp1[0])
        radius = 3500

        #Random start positions
        start_pos = list(range(len(players)))
        print(start_pos)
        import random
        random.shuffle(start_pos)

        for i,p in enumerate(players):
            import random
            rand = random.randint(0,5)
            idx = start_pos[i]
            sign = 1 if idx % 2 == 0 else -1
            angle_pod = angle + np.deg2rad(15 + rand)*(idx+1)/2*sign
            x = cp1[0] + rand +radius * np.cos(angle_pod + math.pi)
            y = cp1[1] + rand + radius * np.sin(angle_pod + math.pi)
            theta = angle_pod


            #x = 8000 + 2000 * math.cos(theta)
            #y = 4500 + 2000 * math.sin(theta)
            team = i % 2 if is_teams else i
            player_advanced = PlayerAdvanced(p, is_dual_pod, "RACE")
            player_elemination = PlayerRace(player_advanced, self.simulator, self.visualization, i, x, y, theta, team, is_dual_pod, checkpoints, checkpoint_radius, is_teams)
            self.game_players.append(player_elemination)


