
import collections
import math
from time import time
from typing import Collection
import numpy as np
from numpy.lib.type_check import real
from numpy.linalg.linalg import norm



class UFO: 
    
    RADIUS = 400 #
    PARTITION_OF_DIRECTION_VECTOR = 1-0.15
    SPEED_MULTIPLIER = 50
    THRUST_VECTOR_LENGTH = (1-PARTITION_OF_DIRECTION_VECTOR) * SPEED_MULTIPLIER
    MAX_ANGULAR_CHANGE = np.deg2rad(18)

    SHIELD_MASS_MULTIPLYER = 10
    STANDARD_MASS = 120


    boost_charging = 0

    shield_counter = 0
    shield_charging = 0

    position =np.array((0,0))
    old_pos = np.array((0,0))
    direction_vector = np.array((0,0))
    direction_thrust_vector = np.array((0,0))

    angle = 0
    velosity = 0
    
    def __init__(self, position, angle):
        self.position = np.array((position[0],position[1])) 
        self.old_pos = np.array((position[0],position[1])) 
        self.angle = angle
        self.velosity = 0
        self.direction_thrust_vector = np.array((math.cos(angle), math.sin(angle)))
        self.direction_vector =np.array((math.cos(self.angle), math.sin(self.angle)))
        self.mass =  self.STANDARD_MASS
        #print(self.direction_vector)

    # velosity pr sec

    def update_position(self, position): 
        self.old_pos = self.position
        self.position = position

    def update_direction_vecotor(self, direction_vector):
        self.direction_vector = direction_vector
        self.velosity = math.sqrt(direction_vector[0]**2 + direction_vector[1]**2)
        #self.angle = math.atan2(direction_vector[1], direction_vector[0])

    def backwards_vector_due_to_football(self, pos, football, overlap):
        
            vector_pos_to_football = football.position- pos 
            norm_pos_to_football = np.linalg.norm(vector_pos_to_football)
            bacwards_direction_vector = self.position - pos

            norm_bacwards_direction_vector = np.linalg.norm(bacwards_direction_vector)
            dot_product = np.dot( bacwards_direction_vector/norm_bacwards_direction_vector, vector_pos_to_football/ norm_pos_to_football)  
        
            angleA = np.arccos(dot_product)    
            a = self.RADIUS + football.RADIUS - overlap
            b = norm_pos_to_football
            angleB = np.arcsin(b*np.sin(angleA)/a)

            angleC = np.pi - angleA- angleB
            #cosin-relation c^2 = a^2+ b^2 - 2ab cos(C)
            move_backward = np.sqrt(a**2 + b**2 - 2*a*b*np.cos(angleC))
            
        
            resulting_bacwards_direction_vector = - self.direction_vector*move_backward/ np.linalg.norm(self.direction_vector)

            return resulting_bacwards_direction_vector 


    def step_simulation(self, delta_time, football):
        x = self.position[0] + self.direction_vector[0]*delta_time
        y = self.position[1]+ self.direction_vector[1]*delta_time
        pos = np.array((x, y))
        if football is not None:
            overlap = 10
            old_distance_to_football = np.hypot(*(self.position - football.position)) 
            distance_to_football = np.hypot(*(pos - football.position)) 
            if old_distance_to_football > distance_to_football:
                if distance_to_football  < self.RADIUS + football.RADIUS - overlap:
                 

                    bacwards_direction_vector = self.backwards_vector_due_to_football(pos, football, overlap)
                    if np.linalg.norm(bacwards_direction_vector) < np.linalg.norm(self.direction_vector*delta_time):
                        pos = pos + bacwards_direction_vector
                    else: 
                        pos = self.position

        self.old_pos = self.position
        self.position = pos
        self.velosity = math.sqrt(self.direction_vector[0]**2 + self.direction_vector[1]**2)
        #self.angle = math.atan2(self.direction_vector[1], self.direction_vector[0])


    def update_vectors(self, target_x, target_y, thrust):
        relative_x = target_x-self.position[0]
        relative_y = target_y-self.position[1]

        angular_target = math.atan2(relative_y, relative_x)
        angular_change = self.angle-angular_target

        angular_change = math.atan2(math.sin(angular_change), math.cos(angular_change))


        if angular_change > self.MAX_ANGULAR_CHANGE: 
            angular_target = self.angle - self.MAX_ANGULAR_CHANGE
        elif angular_change < - self.MAX_ANGULAR_CHANGE: 
            angular_target = self.angle + self.MAX_ANGULAR_CHANGE
        thrust_vector = np.array((math.cos(angular_target)*self.THRUST_VECTOR_LENGTH*thrust, math.sin(angular_target)*self.THRUST_VECTOR_LENGTH*thrust))
        
        self.angle = math.atan2(thrust_vector[1], thrust_vector[0])
        self.direction_thrust_vector = thrust_vector
        
        resuling_vector = np.array((self.direction_vector[0]*self.PARTITION_OF_DIRECTION_VECTOR + thrust_vector[0], self.direction_vector[1]*self.PARTITION_OF_DIRECTION_VECTOR + thrust_vector[1]))
        self.direction_vector = resuling_vector

        #print("vel:", np.linalg.norm(resuling_vector))
        
    
    def update_target(self, target_x, target_y, thrust): 
        if self.shield_charging > 0: 
            self.shield_charging -= 1

        if self.shield_counter == 0 and self.mass > self.STANDARD_MASS: 
            self.mass = self.STANDARD_MASS

        elif self.shield_counter > 0: 
            self.shield_counter -= 1
            return

        if thrust == "SHIELD":
            if self.shield_charging == 0: 
                self.shield_charging = 100
                self.shield_counter = 10
                self.mass = self.STANDARD_MASS*self.SHIELD_MASS_MULTIPLYER
                return
            thrust = 0

        if self.boost_charging > 0:
            self.boost_charging -= 1 

        if thrust == "BOOST":
            if self.boost_charging == 0: 
                thrust = 650
                self.boost_charging = 200
            else: 
                thrust = 100
        

        self.update_vectors(target_x, target_y, thrust)
        

class Football: 

    FIELD_HEIGHT = 9000
    FIELD_WIDHT = 16000

    
    FRICTION = 0.85
    RADIUS = 800
    MIN_VELOCITY = 10

    mass = 30

    position =np.array((0,0))
    direction_vector = np.array((0,0))

    def __init__(self, position): 
        self.position = position

    def update_velocity(self): 
        if np.linalg.norm(self.direction_vector) < self.MIN_VELOCITY: 
             self.direction_vector = np.array((0,0))
        else: 
            self.direction_vector = self.direction_vector * self.FRICTION

    
    def update_direction_vecotor(self, direction_vector):
        self.direction_vector = direction_vector


    def step_simulation(self, delta_time):
        x = self.position[0] + self.direction_vector[0]*delta_time
        y = self.position[1]+ self.direction_vector[1]*delta_time

        # Make the Particles bounce off the walls
        if x - self.RADIUS < 0:
            x = self.RADIUS
            self.direction_vector[0] = -self.direction_vector[0]
        if x + self.RADIUS > self.FIELD_WIDHT:
            x = self.FIELD_WIDHT-self.RADIUS
            self.direction_vector[0] = -self.direction_vector[0]
        if y - self.RADIUS < 0:
            y = self.RADIUS
            self.direction_vector[1] = -self.direction_vector[1]
        if y + self.RADIUS > self.FIELD_HEIGHT:
            y = self.FIELD_HEIGHT-self.RADIUS
            self.direction_vector[1] = -self.direction_vector[1]

        self.position = np.array((x, y))
       






class Simulator:

    ufo_list = [UFO]
    MAX_TIME_STEP = 0.0025 

    #col = False

    def __init__(self):
        self.ufo_list = []
        self.football = None
    
    def add_football(self, position):        
        self.football = Football(position)
     
    def add_ufo(self, position, angle):        
        self.ufo_list.append(UFO(position, angle))
        return len(self.ufo_list)-1


    def update_targets(self, target_x_list, target_y_list, thrust_list):
        for i, ufo in enumerate(self.ufo_list): 
            ufo.update_target(target_x_list[i], target_y_list[i], thrust_list[i])
        
        if self.football is not None:
            self.football.update_velocity()
        


    def step_simulation(self, delta_time):
        
        n_steps = int(math.ceil(delta_time / self.MAX_TIME_STEP))
        n_steps = max(1, n_steps)
        time_step = delta_time / n_steps
        # print ("simulator ran {} of time {:0.2f}ms".format(n_steps, time_step * 1000))
        for step in range(0, n_steps):
            if self.football is not None:
                self.football.step_simulation(time_step)
            #print("step simulation")
            for i, ufo in enumerate(self.ufo_list): 
                ufo.step_simulation(time_step, self.football)

            self.handle_collisions()
            


    def update_direction_vector(self, element, direction_vectors):
        if len(direction_vectors) == 0: 
            return
        direction_vector = np.array((0,0))
        for vector in direction_vectors: 
            direction_vector = direction_vector + vector
        element.update_direction_vecotor(direction_vector)


    def is_overlap(self, element1, element2):
        overlap = np.hypot(*(element1.position - element2.position))
        if overlap < element1.RADIUS + element2.RADIUS: 
            time_difference = 0.001
            pos1 = element1.position + element1.direction_vector*time_difference
            pos2 = element2.position + element2.direction_vector*time_difference
            new_overlap= np.hypot(*(pos1 - pos2))
            if new_overlap <= overlap: 
                return True
        return False


       
    def handle_collisions(self):
        number_collistion = [0 for i in range(len(self.ufo_list))]

        for i in range(len(self.ufo_list)): 
            for j in range(i+1, len(self.ufo_list)):
                if self.is_overlap(self.ufo_list[i], self.ufo_list[j]): 
                #overlap = np.hypot(*(self.ufo_list[i].position - self.ufo_list[j].position))
                #if overlap < 2*self.ufo_list[i].RADIUS:
                    number_collistion[i] +=1
                    number_collistion[j] +=1

        new_direction_vectors =[[] for i in range(len(self.ufo_list))]
        if self.football is not None:
            football_direction_vectors = []
            football_collistion = 0
            for i in range(len(self.ufo_list)): 
                if self.is_overlap(self.ufo_list[i], self.football):
                #overlap = np.hypot(*(self.ufo_list[i].position - self.football.position))
                #if overlap < self.ufo_list[i].RADIUS +self.football.RADIUS:
                    number_collistion[i] +=1
                    football_collistion +=1
                
            for i in range(len(self.ufo_list)):
                if self.is_overlap(self.ufo_list[i], self.football):
                #overlap = np.hypot(*(self.ufo_list[i].position - self.football.position)) 
                #if overlap < self.ufo_list[i].RADIUS +self.football.RADIUS:
                    ufo_direction_vector, football_direction_vector = self.change_velocities(self.ufo_list[i], self.football, number_collistion[i], football_collistion)
                    football_direction_vectors.append(football_direction_vector)
                    new_direction_vectors[i].append(ufo_direction_vector)

            self.update_direction_vector(self.football, football_direction_vectors) 


        for i in range(len(self.ufo_list)): 
            for j in range(i+1, len(self.ufo_list)):
                if self.is_overlap(self.ufo_list[i], self.ufo_list[j]): 
                #overlap = np.hypot(*(self.ufo_list[i].position - self.ufo_list[j].position))
                #if overlap < 2*self.ufo_list[i].RADIUS:
                    direction1, direction2 = self.change_velocities(self.ufo_list[i], self.ufo_list[j], number_collistion[i], number_collistion[j])
                    new_direction_vectors[i].append(direction1)
                    new_direction_vectors[j].append(direction2)

        for i in range(len(self.ufo_list)): 
            self.update_direction_vector(self.ufo_list[i], new_direction_vectors[i]) 



        
    def get_football_state(self):
        return self.football.position
    

    def get_ufo_state(self,i):
        return self.ufo_list[i].position, self.ufo_list[i].angle, self.ufo_list[i].mass > self.ufo_list[i].STANDARD_MASS
    


    def change_velocities(self, obj1, obj2, n_col1 = 1, n_col2 = 1 ):
            """
            Particles p1=obj1 and p2=obj2 have collided elastically: update their
            velocities.

            """

            m1, m2 = obj1.mass, obj2.mass
            M = m1 + m2
            r1, r2 = obj1.position, obj2.position
            d = np.linalg.norm(r1 - r2)**2
            v1, v2 = obj1.direction_vector/n_col1, obj2.direction_vector/n_col2
            u1 = v1 - (2*m2 / M) * (np.dot(v1-v2, r1-r2) / d) * (r1 - r2)
            u2 = v2 - (2*m1 / M) * (np.dot(v2-v1, r2-r1) / d) * (r2 - r1)
            return u1,u2

    

    






    
