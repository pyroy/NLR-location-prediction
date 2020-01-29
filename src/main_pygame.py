from tkinter import *
from tkinter.ttk import *
from nodes import *

# Node position is in hundreds of meters.

import algorithms.astar
import algorithms.ruh
import algorithms.bayesian_ruh
import algorithms.giraffe

import location_selection

import os, pickle, math, random, copy, pygame
import numpy as np

pygame.font.init()
font = pygame.font.SysFont('Impact', 20)

OSMInterface = OSMInterfaceOBJ()

class MainApp(Frame):

    def __init__(self):
        super().__init__()
        
        self.offset = (0, 0)
        self.scale = 7
        self.origin_lat = 0
        self.origin_lon = 0
        self.canvas_width = 500
        self.canvas_height = 500
        self.nn = None
        self.gn = None
        self.mn = None
        self.paths = {}
        self.visited = {}
        self.times = {}
        self.goal_vector = {}
        
        self.initUI()

    def load_maps(self):
    
        print("loading bremm...")
        OSMInterface.load_location("Bremm")
        self.make_render( "Bremm" )

        A = {}
        A["area"] = ("greaterthan", 0.01011135)
        A["bruhhhhhhhhhhhhhhhhhhhhh"] = ["highway", "railway", "waterway", "natural"]
        goals = location_selection.query(OSMInterface, A)
        m = 1/len(goals)

        #self.goal_vector = {OSMInterface.get_int_from_node(g).ref: m for g in goals}
        
        #print("loading heilbronn...")
        #OSMInterface.load_location("Heilbronn",  origin = (9.1753, 49.1582) )
        #self.make_render( "Heilbronn" )
        
        #print("loading oberhausen...")
        #OSMInterface.load_location("Oberhausen", origin = (6.8224, 51.4868) )
        #self.make_render( "Oberhausen" )
        
        print("done.")
        self.cnv.fill( (128,128,128) )

    def map_coords_to_pixel_coords(self, pos):
        return (self.scale*pos[0] + self.offset[0], self.scale*pos[1] + self.offset[1])
        
    def mtp(self, pos):
        return (int(self.scale*pos[0] + self.offset[0]), int(self.scale*pos[1] + self.offset[1]))
        
    def pixel_coords_to_map_coords(self, pos):
        return ((pos[0] - self.offset[0])/self.scale, (pos[1] - self.offset[1])/self.scale)
        
    def ptm(self, pos):
        return ((pos[0] - self.offset[0])/self.scale, (pos[1] - self.offset[1])/self.scale)

    def run_alg(self):
        self.visited = algorithms.bayesian_ruh.bruh(OSMInterface, self.nn, self.goal_vector)
        self.paths = {}
        for goal in self.goal_vector.keys():
            print(self.nn, OSMInterface.get_node_from_id( goal ))
            self.paths[ goal ] = algorithms.astar.astar( OSMInterface, self.nn, OSMInterface.get_node_from_id( goal ) )
        print(list(self.paths.keys()))

    def make_begin(self):
        self.nn = OSMInterface.get_nearest_node_to( self.ptm( (250, 250) ) )
        self.run_alg()
        
    def addgoal(self):
        g = OSMInterface.get_nearest_node_to( self.ptm( (250, 250) ) )
        l = len( self.goal_vector.keys() )
        
        for gn, p in self.goal_vector.items():
            self.goal_vector[ gn ] = p * l/(l + 1)
    
        self.goal_vector[ g.ref ] = 1/(l + 1)
        self.run_alg()
        
        print(self.goal_vector, self.visited)
    
    def addsighting(self):
        s = OSMInterface.get_nearest_node_to( self.ptm( (250, 250) ) )
        self.goal_vector = algorithms.bayesian_ruh.bruh_update(OSMInterface, self.nn, s, self.goal_vector)
        self.run_alg()
        print(self.goal_vector)
        
    def resetsightings(self):
        l = len(self.goal_vector.keys())
        
        for g, p in self.goal_vector.items():
            self.goal_vector[ g ] = 1/l
        
        self.run_alg()
        print(self.goal_vector)

    def make_render(self, location):
        OSMInterface.select_location( location )
        
        x_max = -1
        x_min = 1000000
        y_max = -1
        y_min = 1000000
        
        for Node in OSMInterface.get_unique_intersections():
            
                p = Node.get_pos()
                
                if p[0] > x_max:
                    x_max = p[0]
                elif p[0] < x_min:
                    x_min = p[0]
                if p[1] > y_max:
                    y_max = p[1]
                elif p[1] < y_min:
                    y_min = p[1]
                
        surf_bounds_max = self.mtp( (x_max, y_max) )
        surf_bounds_min = self.mtp( (x_min, y_min) )
        
        self.scale = 35
        
        surf = pygame.Surface( (surf_bounds_max[0]*5 - surf_bounds_min[0]*5, surf_bounds_max[1]*5 - surf_bounds_min[1]*5))
        surf.fill( (255,255,255) )
        pygame.draw.rect(surf, (0,0,0,120), (0, 0, surf.get_width(), surf.get_height()), 2)
        for street_id, intersecting_nodes in OSMInterface.get_intersections().items():

            for i in range( len(intersecting_nodes) - 1 ):
            
                from_node = OSMInterface.get_node_from_id( intersecting_nodes[i] )
                from_node_scaled = self.mtp( from_node.get_pos() )
                
                to_node   = OSMInterface.get_node_from_id( intersecting_nodes[i+1] )
                to_node_scaled = self.mtp( to_node.get_pos() )

                if OSMInterface.check_features(from_node, to_node, {}):
                    pygame.draw.line(surf, (0,0,0), from_node_scaled, to_node_scaled, 2)
                                
        OSMInterface.RENDERS[ location.lower() ] = surf
        
        self.scale = 7

    def showmap(self):
        OSMInterface.select_location( self.location_selection_dropdown.get() )
        
        self.cnv.fill( pygame.Color(255,255,255) )
        n_image = OSMInterface.RENDERS[ self.location_selection_dropdown.get().lower() ]
        if self.scale > 9:
            n_size = (500/self.scale*35, 500/self.scale*35)
            network_image = pygame.Surface(n_size)
            network_image.fill( (255,255,255) )
            network_image.blit(n_image, (0,0), (-self.offset[0]/self.scale*35, -self.offset[1]/self.scale*35, n_size[0], n_size[1]))
            self.cnv.blit( pygame.transform.smoothscale(network_image, (500, 500)), (0,0))
        else:
            self.cnv.blit( pygame.transform.smoothscale(n_image, (int(n_image.get_width()*self.scale/35), int(n_image.get_height()*self.scale/35))), self.offset )

        #for node in OSMInterface.get_unique_intersections():
        #        node_scaled = self.mtp( node.get_pos()  )
        #        pygame.draw.circle(self.cnv, (255,0,0), node_scaled, int(self.scale/7))
                
        for node_id, val in self.visited.items():
            g = self.visited[node_id]
            color = (255 - 255*g, 255*g, 0)
            pygame.draw.circle(self.cnv, color, self.mtp( OSMInterface.get_node_from_id(node_id).get_pos() ), 4)

        self.mn = OSMInterface.get_nearest_node_to( self.ptm( (250, 250) ) )
                     
        if pygame.key.get_focused():
            pygame.draw.circle(self.cnv, (0,0,255), (250,250), 3)
        else: pygame.draw.circle(self.cnv, (0,0,0), (250,250), 3)
        
        for i in range(len(self.goal_vector.keys())):
            textsurface = font.render('{}%'.format(int(100*self.goal_vector[list(self.goal_vector.keys())[i]])), False, (0, 0, 0))
            p = self.mtp( OSMInterface.get_node_from_id(list(self.goal_vector.keys())[i]).get_pos() )
            self.cnv.blit(textsurface, p)

        for g, p in self.paths.items():
            for i in range(len(p)-1):
                b = p[i]
                e = p[i + 1]
                pygame.draw.line(self.cnv, (0,0,0), self.mtp(b.get_pos()), self.mtp(e.get_pos()), 4)

        #m = 550501670
        #p = 527798548 
        #print(OSMInterface.get_node_from_id(p).lat, OSMInterface.get_node_from_id(p).lon)
        #w = OSMInterface.get_streets()[ m ]
        #pygame.draw.polygon(self.cnv, (255,0,255), [self.mtp( OSMInterface.get_node_from_id(node).get_pos() ) for node in w])

        #for polygon in OSMInterface.get_polygons():
        #    for way in polygon:
        #        if int(way) in OSMInterface.get_streets().keys() and len(OSMInterface.get_streets()[ int(way) ]) > 2:
        #            color = (random.randint(0,255), random.randint(0,255), random.randint(0,255))
        #            pygame.draw.polygon(self.cnv, color, [self.mtp( OSMInterface.get_node_from_id(node).get_pos() ) for node in OSMInterface.get_streets()[ int(way) ]])


    def moveup(self, step=40):
        self.offset = (self.offset[0], self.offset[1] + step)

    def movedown(self, step=40):
        self.offset = (self.offset[0], self.offset[1] - step)

    def moveleft(self, step=40):
        self.offset = (self.offset[0] + step, self.offset[1])

    def moveright(self, step=40):
        self.offset = (self.offset[0] - step, self.offset[1])

    def zoomin(self, step=1):
        t_o = self.ptm( (250,250) )
        self.scale += step
        self.offset = (self.offset[0] + 250 - self.mtp(t_o)[0], self.offset[1] + 250 - self.mtp(t_o)[1])

    def zoomout(self, step=1):
        t_o = self.ptm( (250,250) )
        self.scale -= step
        self.offset = (self.offset[0] + 250 - self.mtp(t_o)[0], self.offset[1] + 250 - self.mtp(t_o)[1])

    def update_pygame_screen(self):
        pygame.display.flip()
        
        if pygame.key.get_pressed()[pygame.K_RIGHT ]: self.moveright(5)
        if pygame.key.get_pressed()[pygame.K_LEFT  ]: self.moveleft (5)
        if pygame.key.get_pressed()[pygame.K_UP    ]: self.moveup   (5)
        if pygame.key.get_pressed()[pygame.K_DOWN  ]: self.movedown (5)
        if pygame.key.get_pressed()[pygame.K_EQUALS]: self.zoomin   (0.5)
        if pygame.key.get_pressed()[pygame.K_MINUS ]: self.zoomout  (0.5)
        
        self.showmap()
        
        self.after(16, lambda: self.update_pygame_screen() )

    def printloc(self):
        print(self.mn.ref)
        print(self.mn.lat, self.mn.lon)
        print(self.mn.get_pos())

    def initUI(self):
    
        self.master.title("Primitive OSM Explorer")
        self.pack(fill=BOTH, expand=True)

        frame = Frame(self)
        frame.pack()

        self.location_selection_dropdown = StringVar(self)
        self.inp1 = OptionMenu(frame, self.location_selection_dropdown, 'Bremm', 'Bremm', "Heilbronn", "Oberhausen")
        self.inp1.pack(side=LEFT, padx=10)

        button1 = Button(frame, text="Set as start", command=self.make_begin)
        button1.pack(side=LEFT)

        button1 = Button(frame, text="Get location", command=self.printloc)
        button1.pack(side=LEFT)
        
        frameg = Frame(self)
        frameg.pack()
        
        button1 = Button(frameg, text="Add as goal", command=self.addgoal)
        button1.pack(side=LEFT)
        
        button1 = Button(frameg, text="Update with node as sighting", command=self.addsighting)
        button1.pack(side=LEFT)
        
        button1 = Button(frameg, text="Reset sightings", command=self.resetsightings)
        button1.pack(side=LEFT)

        frame2 = Frame(self, relief=RAISED)
        frame2.pack()

        embed = Frame(frame2, width = 500, height = 500) #creates embed frame for pygame window
        embed.pack()
        embed.focus_set()
        os.environ['SDL_WINDOWID'] = str(embed.winfo_id())
        os.environ['SDL_VIDEODRIVER'] = 'windib' # black magic to let pygame draw onto the embed
        self.cnv = pygame.display.set_mode( (500,500) )
        self.cnv.fill( pygame.Color(255,255,255) )
        pygame.display.init()
        pygame.display.update()

        frame3 = Frame(self)
        frame3.pack()
        
        button2 = Button(frame3, text="Move Left", command=self.moveleft)
        button2.pack(side=LEFT)

        button3 = Button(frame3, text="Move Right", command=self.moveright)
        button3.pack(side=LEFT)

        button4 = Button(frame3, text="Move Up", command=self.moveup)
        button4.pack(side=LEFT)

        button5 = Button(frame3, text="Move Down", command=self.movedown)
        button5.pack(side=LEFT)

        button6 = Button(frame3, text="Zoom In", command=self.zoomin)
        button6.pack(side=LEFT, padx=(20, 0))

        button7 = Button(frame3, text="Zoom Out", command=self.zoomout)
        button7.pack(side=LEFT)
        
        def change_dropdown(*args):
            self.goal_vector = {}
            self.nn = None

        # link function to change dropdown
        self.location_selection_dropdown.trace('w', change_dropdown)
        
        # tkinter updates, then loads the maps. This is so that we can display the text before we load in all the maps
        self.after(100, lambda: self.load_maps() )
        
        self.after(100, lambda: self.update_pygame_screen() )

def main():
    root = Tk()
    root.geometry("530x560")
    root.resizable(False, False)
    app = MainApp()
    root.mainloop()

if __name__ == '__main__':
    main()
