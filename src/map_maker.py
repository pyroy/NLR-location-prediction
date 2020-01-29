from nodes import *

import algorithms.astar
import algorithms.ruh
import algorithms.bayesian_ruh
import algorithms.giraffe

import location_selection
import feature_dict

import os, pickle, math, random
import numpy as np

import folium, webbrowser

OSMInterface = OSMInterfaceOBJ()

def rgb_to_hex(rgb):
    return '%02x%02x%02x' % rgb

def query(vehicle_features, goal_features, sightings, view_time, start_pos, location):

    print("Loading {}...".format(location))
    OSMInterface.load_location( location )
    mapm = folium.Map(location=OSMInterface.l_min, zoom_start=14)

    path = os.path.dirname(os.path.abspath(__file__)) + "\\"
    path = path[:-4]

    print("Selecting possible locations...")
    goals = location_selection.query(OSMInterface, goal_features)
    prior = 1/len(goals) # uniforme prior pls update

    goal_vector = {OSMInterface.get_int_from_node(g).ref: prior for g in goals}
    #p = OSMInterface.get_nearestll( (50.099239, 7.119022) )
    #goal_vector = {OSMInterface.get_int_from_node(p.ref).ref: 1}
    
    print("Retrieving starting node...")
    start_node = OSMInterface.get_nearestll( start_pos )
    
    print("Updating with all sightings...")
    for sighting in sightings:
        s = OSMInterface.get_nearestll( sighting[1] )
        goal_vector = algorithms.bayesian_ruh.bruh_update(OSMInterface, start_node, s, goal_vector, time=sighting[0], features=vehicle_features)
    
    print("Running giraffe...")
    node_values = algorithms.bayesian_ruh.bruh(OSMInterface, start_node, goal_vector, time=view_time, time_s=0.1, dist_s=20, features=vehicle_features)
    
    print("Running astar...")
    paths = {}
    for goal in goal_vector.keys():
        p = algorithms.astar.astar( OSMInterface, start_node, OSMInterface.get_node_from_id( goal ), features=vehicle_features )
        if p != [] and p is not None:
            paths[ goal ] = p
        
    print("Generating map HTML...")
    for street_id, intersecting_nodes in OSMInterface.get_intersections().items():
        for i in range( len(intersecting_nodes) - 1 ):
        
            from_node = OSMInterface.get_node_from_id( intersecting_nodes[i] )
            to_node   = OSMInterface.get_node_from_id( intersecting_nodes[i+1] )

            if not OSMInterface.check_features(from_node, to_node, vehicle_features):
                break
            
            try: g = node_values[to_node.ref]
            except: g = 0
            
            c = "#"+rgb_to_hex( (int(255*(1 - g)), int(255*math.sqrt(g)), 0) ).upper()
            
            #if OSMInterface.check_features(from_node, to_node, vehicle_features):
            folium.vector_layers.PolyLine(color=c, locations=[(from_node.lat, from_node.lon), (to_node.lat, to_node.lon)]).add_to(mapm)
                
    for g, p in goal_vector.items():
        n = OSMInterface.get_int_from_node(g)
        c = "#"+rgb_to_hex( (int(100*math.sqrt(p)), int(100*math.sqrt(p)), int(255*math.sqrt(p))) ).upper()
        folium.Circle(
            radius=max(30,600*p),
            location=(n.lat, n.lon),
            color=c,
            fill=True,
            tooltip="{}%".format(int(1000*p)/10),
        ).add_to(mapm)
        text="Goal"
        folium.Marker(
            location=(n.lat, n.lon),
            color=c,
            icon=folium.features.DivIcon(
                icon_size=(len(text)*9, 36),
                icon_anchor=(0,36),
                html='<div style="text-align: center"><h1 style="font-size: 13pt; color: white; background-color: black">{}</h1></div>'.format(text),
            )
        ).add_to(mapm)
                
    for goal, way in paths.items():
        for i in range( len(way) - 1 ):
            from_node = way[i]
            to_node   = way[i+1]
            folium.vector_layers.PolyLine(color='black', locations=[(from_node.lat, from_node.lon), (to_node.lat, to_node.lon)]).add_to(mapm)
            
    folium.Circle(
        radius=80,
        location=(start_node.lat, start_node.lon),
        color='aqua',
        fill=True,
    ).add_to(mapm)
    
    text="Start at t=0h"
    folium.Marker(
        location=(start_node.lat, start_node.lon),
        color='aqua',
        icon=folium.features.DivIcon(
            icon_size=(len(text)*9, 36),
            icon_anchor=(0,36),
            html='<div style="text-align: center"><h1 style="font-size: 13pt; color: aqua; background-color: black">{}</h1></div>'.format(text),
        )
    ).add_to(mapm)
    
    for sighting in sightings:
        s = OSMInterface.get_nearestll( sighting[1] )
        folium.Circle(
            radius=80,
            location=(s.lat, s.lon),
            color='purple',
            fill=True,
        ).add_to(mapm)
        text="Sighting at t={}h".format(sighting[0])
        folium.Marker(
            location=(s.lat, s.lon),
            color='purple',
            icon=folium.features.DivIcon(
                icon_size=(len(text)*9, 36),
                icon_anchor=(0,36),
                html='<div style="text-align: center"><h1 style="font-size: 13pt; color: green; background-color: black">{}</h1></div>'.format(text),
            )
        ).add_to(mapm)
    
    mapm.add_child(folium.LatLngPopup())
        
    mapm.save(path+"maps\\map.html")
    webbrowser.open(path+"maps\\map.html")
    
if __name__ == "__main__":
    query(feature_dict.FEATURES_FIETS, {"area": ("greaterthan", 1)}, [(0.2, (50.105969, 7.125105)), (0.4, (50.1065, 7.1493))], 0.5, (50.081804, 7.130481), 'bremm')
    #query({}, {"area": ("greaterthan", 1)}, [], 0.5, (50.081804, 7.130481), 'bremm')
    #query({}, {"area": ("greaterthan", 5)}, [], 0.5, (49.141961, 9.223089), 'heilbronn')
