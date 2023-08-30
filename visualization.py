from os import path
import matplotlib.pyplot as plt
import matplotlib.patches as patches
from matplotlib import animation
import matplotlib.image as mpimg
import numpy

class UfoComponent:
    player_colors = ['blue', 'magenta', 'red', 'green', 'yellow', 'cyan', 'orange', 'silver', 'lime', 'purple' ]
    wedge_colors = ['palegreen', 'deepskyblue', 'red', 'green', 'yellow', 'cyan', 'orange', 'silver', 'lime', 'purple' ]
    
    def __init__(self, player_index, position, radius, callback, is_teams = False):
        self.circle = patches.Circle(position, radius)
        self.wedge = patches.Wedge(position, radius, 0, 90)
        #self.wedge.set_color(UfoComponent.wedge_colors[1]) 

        self.callback = callback  
        if is_teams: 
            self.circle.set_color(UfoComponent.player_colors[player_index%2])
            self.wedge.set_color(UfoComponent.wedge_colors[player_index]) 
        else:
            self.circle.set_color(self.player_colors[player_index])

    def update(self):
        position, angle, shield = self.callback()
        self.circle.set_center(position)
        self.wedge.set_center(position)
        theta1 = numpy.rad2deg(angle + numpy.pi - numpy.pi/4)
        theta2 = numpy.rad2deg(angle + numpy.pi + numpy.pi/4)
        self.wedge.set_theta1(theta1)
        self.wedge.set_theta2(theta2)
        self.circle.set_fill(not shield)

    def get_patches(self):
        return [self.circle, self.wedge]

class CheckpointComponent:
    def __init__(self, position, radius):
        self.circle = patches.Circle(position, radius, color='y', fill=False)

    def update(self):
        pass

    def get_patches(self):
        return [self.circle]

class FootballComponent:
    def __init__(self, position, radius, callback):
        self.circle = patches.Circle(position, radius, color='y', fill=False)
        self.callback = callback

    def update(self):
        position = self.callback()
        self.circle.set_center(position)

    def get_patches(self):
        return [self.circle]

class LineComponent:
    def __init__(self, positions):
        self.polygon = patches.Polygon(positions, color='y', fill=False)

    def update(self):
        pass

    def get_patches(self):
        return [self.polygon]


class Visualization:
    def __init__(self, simulation_callback, players, is_team = False):

        self.simulation_callback = simulation_callback
        self.components = []

        FIELD_WIDTH = 16000
        FIELD_HIGHT = 9000

        self.fig = plt.figure()

        self.patchs = []
        self.txt_components = []
        
        number_rows = 10
        number_cols = 1
        self.text_field = self.fig.add_subplot(number_rows,number_cols,1, aspect='equal')
        self.text_field.set_xlim(0, FIELD_WIDTH)
        self.text_field.set_ylim(0, FIELD_HIGHT/number_rows)
        self.text_field.axis('off')
        self.create_text(players, is_team)
        

        self.field = self.fig.add_subplot(number_rows,number_cols,(2,number_rows), aspect='equal')
        self.field.set_xlim(0, FIELD_WIDTH)
        self.field.set_ylim(0, FIELD_HIGHT)
        # self.field.axis('off')

        img = mpimg.imread('./night-311.png')
        self.field.imshow(img, interpolation='none', zorder=0, extent=(0,FIELD_WIDTH, 0, FIELD_HIGHT))

        frame_delay_ms = 50

        self.anim = animation.FuncAnimation(self.fig, self.animate, 
                        interval=frame_delay_ms, 
                        repeat=False, blit=True)
        self.winner = None
        self.stop = False



    def create_text(self, players, is_team = False):        
        x_max = int(self.text_field.get_xlim()[1])
        y_max = int(self.text_field.get_ylim()[1])
        half_players = int(numpy.ceil(len(players)/2))
        space_for_name = x_max*2/(len(players))
        radius_of_pach = (y_max*9/10) / 4

        for i in range(half_players):
            x = radius_of_pach + i*space_for_name
            y = y_max*3/4
            ufo_component = UfoComponent(i, [x,y], radius_of_pach, None, is_team)
            self.add_component_text(ufo_component)
            self.text_field.text(radius_of_pach*2 + i*space_for_name+100,  y_max*2/3 , players[i].name, fontsize = 'large')
        
        for i in range(half_players, len(players)):
            j = (i-half_players)
            x= radius_of_pach + j*space_for_name
            y =y_max/4
            ufo_component = UfoComponent(i, [x,y], radius_of_pach, None, is_team)
            self.add_component_text(ufo_component)
            self.text_field.text(radius_of_pach*2 + j*space_for_name +100 ,y_max*1/8, players[i].name, fontsize = 'large')
            
  


    def add_component(self, component):
        self.components.append(component)
        for patch in component.get_patches():
            p=self.field.add_patch(patch)
            self.patchs.append(p)

    def add_component_text(self, component):
        for patch in component.get_patches():
            t = self.text_field.add_patch(patch)


    def set_winner(self, text):
        self.winner = text

    def animate(self, i):
        if self.stop:
            exit(1)
            return self.patchs


        self.simulation_callback()

        #import time
        #time.sleep(0.001)
        # plt.draw_idle()


        for c in self.components:
            c.update()
                   

        if i> 2000 or self.winner is not None:
            if self.winner is None: 
                print("Draw")
                self.text_field.text(0, 1000, "Draw", fontsize = 'xx-large')
                self.anim.event_source.stop()
                self.stop = True
            else:
                self.text_field.text(0, 1000, "Winner is: {}".format(self.winner), fontsize = 'xx-large')
                print("Winner is: {}".format(self.winner))
                plt.get_current_fig_manager().full_screen_toggle()
                self.anim.event_source.stop()
                self.stop = True
                # ToDo add text         
        return self.patchs

    def run(self):
        
        #plt.get_current_fig_manager().full_screen_toggle()
        plt.draw()
        plt.waitforbuttonpress(0) # this will wait for indefinite time
        plt.close(self.fig)
        #plt.show()

    






