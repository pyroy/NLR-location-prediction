import osmnx as ox
import networkx as nx
import folium

import os
path = os.path.dirname(os.path.abspath(__file__)) + "\\"
path = path[:-5]

G = ox.graph_from_file(path+"maps\\bremm.osm")
K = ox.graph_from_place('Amersfoort,NL', network_type='drive')
Z = ox.graph_from_place('NL', network_type='drive')
H = ox.graph_from_place('Bremm,GER', network_type='drive')


# origin = ox.geo_utils.geocode('KROAST,Amersfoort, NL')
# destination = ox.geo_utils.geocode('krakelingtunnel,Almere, NL')
# orig = ox.get_nearest_node(Z, origin)
# dest = ox.get_nearest_node(Z, destination)
# route = nx.shortest_path(Z,orig, dest)
# ox.plot_graph_route(Z, route)
#ox.plot_graph(G)\
#ox.plot_graph(ox.project_graph(H));

print("test")

place = {'city': 'Amersfoort',
         'state': 'Utrecht',
         'country': 'NL'}
kaas = ox.graph_from_place(place, network_type='drive')
fig, ax = ox.plot_graph(kaas, fig_height=12, node_size=0, edge_linewidth=0.5)
