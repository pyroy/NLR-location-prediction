from tkinter import *
from tkinter.ttk import *
import os, pickle, math
from nodes import Node, OSMInterfaceOBJ
import pygame
pygame.init()

OSMInterface = OSMInterfaceOBJ()

class MainApp(Frame):

    def __init__(self):
        super().__init__()
        
        self.offset = (0, 100)
        self.scale = 7
        self.origin_lat = 0
        self.origin_lon = 0
        self.canvas_width = 500
        self.canvas_height = 500
        
        self.initUI()

    def load_maps(self):
    
        OSMInterface.load_location("Bremm",      origin = (7.0975, 50.1089) )
        OSMInterface.load_location("Heilbronn",  origin = (9.1753, 49.1582) )
        #OSMInterface.load_location("Oberhausen", origin = (6.8224, 51.4868) )
        
        self.cnv.delete("all")
        
        self.cnv.create_text(self.canvas_width/2, self.canvas_height/2, text= "Please select a map from the dropdown menu.")

    def map_coords_to_pixel_coords(self, pos):
        return (self.scale*pos[0] + self.offset[0], self.scale*pos[1] + self.offset[1])
        
    def mtp(self, pos):
        return (self.scale*pos[0] + self.offset[0], self.scale*pos[1] + self.offset[1])
        
    def pixel_coords_to_map_coords(self, pos):
        return ((pos[0] - self.offset[0])/self.scale, (pos[1] - self.offset[1])/self.scale)
        
    def ptm(self, pos):
        return ((pos[0] - self.offset[0])/self.scale, (pos[1] - self.offset[1])/self.scale)

    def draw_line_scaled(self, pos1, pos2, color="black"):
        self.cnv.create_line( self.mtp(pos1), self.mtp(pos2), fill=color)
        
    def draw_text_scaled(self, pos, text, offset=(0,0), color="black"):
        p = self.mtp(pos)
        self.cnv.create_text(p[0] + offset[0], p[1] + offset[1], text=text, fill=color)

    def showmap(self):
        self.cnv.delete("all")
        
        OSMInterface.select_location( self.location_selection_dropdown.get() )

        # we want to draw the text last to avoid lines drawing over the text
        text_to_create = []
        
        for street_id, intersecting_nodes in OSMInterface.get_intersections().items():
        
            # intersecting_nodes is a list of Node IDs
            for i in range( len(intersecting_nodes) - 1 ):
            
                from_node = OSMInterface.get_node_from_id( intersecting_nodes[i] )
                from_node_scaled = self.mtp( from_node.get_pos() )
                
                to_node   = OSMInterface.get_node_from_id( intersecting_nodes[i+1] )
                to_node_scaled = self.mtp( to_node.get_pos() )
                
                # If the node lies outside the drawing field, don't draw. This speeds up moving the camera when zoomed in.
                if to_node_scaled[0] >= 0 and to_node_scaled[0] <= self.canvas_width:
                    if to_node_scaled[1] >= 0 and to_node_scaled[1] <= self.canvas_height:
                        if from_node_scaled[0] >= 0 and from_node_scaled[0] <= self.canvas_width:
                            if from_node_scaled[1] >= 0 and from_node_scaled[1] <= self.canvas_height:
                            
                                self.draw_line_scaled(from_node.get_pos(), to_node.get_pos(), color="light grey")
                                self.draw_text_scaled(from_node.get_pos(), ".", offset=(0,-3))
                                
                                if "name" in from_node.attributes:
                                    text_to_create.append( (from_node.get_pos(), from_node.get_value("name") ) )

        for text in text_to_create:
            self.draw_text_scaled(text[0], text[1], color="green")
            
        center_map_coords = self.ptm((250, 250))
        
        nn = OSMInterface.get_nearest_node_to( center_map_coords )
        self.draw_text_scaled( center_map_coords, text="O", color="red")
        self.draw_text_scaled( nn.get_pos(), "nearest", color="red")

    def moveup(self):
        self.offset = (self.offset[0], self.offset[1] + 4*self.scale)
        self.showmap()

    def movedown(self):
        self.offset = (self.offset[0], self.offset[1] - 4*self.scale)
        self.showmap()

    def moveleft(self):
        self.offset = (self.offset[0] + 4*self.scale, self.offset[1])
        self.showmap()

    def moveright(self):
        self.offset = (self.offset[0] - 4*self.scale, self.offset[1])
        self.showmap()

    def zoomin(self):
        self.scale += 1
        self.showmap()

    def zoomout(self):
        self.scale -= 1
        self.showmap()

    def initUI(self):
    
        self.master.title("Primitive OSM Explorer")
        self.pack(fill=BOTH, expand=True)

        frame = Frame(self)
        frame.pack()

        self.location_selection_dropdown = StringVar(self)
        self.inp1 = OptionMenu(frame, self.location_selection_dropdown, 'Bremm', 'Bremm', "Heilbronn", "Oberhausen")
        self.inp1.pack(side=LEFT, padx=10)

        button1 = Button(frame, text="Show Nodes", command=self.showmap)
        button1.pack(side=LEFT)

        frame2 = Frame(self, relief=RAISED)
        frame2.pack()

        self.cnv = Canvas(frame2, width=self.canvas_width, height=self.canvas_height)
        self.cnv.pack()
        
        self.cnv.create_text(self.canvas_width/2, self.canvas_height/2, text= "loading maps...")

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
        
        # tkinter updates, then loads the maps. This is so that we can display the text before we load in all the maps
        self.master.after(100, lambda: self.load_maps() )

def main():
    root = Tk()
    root.geometry("530x560")
    root.resizable(False, False)
    app = MainApp()
    root.mainloop()

if __name__ == '__main__':
    main()
