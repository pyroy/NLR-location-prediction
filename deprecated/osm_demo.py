import osmnx as ox

import os
path = os.path.dirname(os.path.abspath(__file__)) + "\\"
path = path[:-5]

G = ox.graph_from_file(path+"maps\\bremm.osm")
ox.plot_graph(G)

print("nieg")
