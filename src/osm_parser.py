import os
from xml.dom import minidom
import pickle
import sys
from nodes import Node

# Gets the root folder of the project
path = os.path.dirname(os.path.abspath(__file__)) + "\\"
path = path[:-4]

# Given a node, outputs all the tags that the corresponding xml contains
def get_node_data(node):
    t = node.getElementsByTagName("tag")
    retdict = {}
    for tag in t:
        key = tag.getAttribute("k")
        val = tag.getAttribute("v")
        retdict[key] = val
    return retdict

def parse_OSM(placename):

    print("converting to DOM...")
    xml = minidom.parse(path+"maps\\{}.osm".format(placename))
    
    nodes = xml.getElementsByTagName('node')
    ways = xml.getElementsByTagName('way')
    relations = xml.getElementsByTagName('relation')

    print("parsing nodes...")

    # NODE_DICT has node references as keys, and a nodes.Node object as the value.
    NODE_DICT = {}
    
    # POLYGON_NODES has way references as keys, and a list of contained node references as the value
    POLYGON_NODES = {}
    
    # POLYGON_TAGS has way references as keys, and a list of all tags containing information about the polygon as value
    POLYGON_TAGS = {}
    
    # INTSEC_DICT has way references as keys, and a list of nodes that are intersections as the value
    INTSEC_DICT = {}

    for node in nodes:
        data = get_node_data( node )

        lat = float(node.getAttribute("lat"))
        lon = float(node.getAttribute("lon"))
        idn = int(node.getAttribute("id"))

        node = (idn, lat, lon)

        NODE_DICT[ idn ] = Node(idn, lat, lon, data)

    print("parsing ways...")

    for way in ways:
        data = get_node_data( way )

        temp = []
        
        for node in way.getElementsByTagName("nd"):
            temp.append( int(node.getAttribute("ref")) )

        POLYGON_NODES[ int(way.getAttribute("id")) ] = temp
        POLYGON_TAGS[ int(way.getAttribute("id")) ] = data

    print("creating node network...")
       
    intersection_node_set = []
    for street_key, street in POLYGON_NODES.items():
        intersection_node_set += street
        
    for node in list(set(intersection_node_set)):
        intersection_node_set.remove(node)
        
    intersection_node_set = list(set(intersection_node_set))
    
    for street_key, street in POLYGON_NODES.items():
        INTSEC_DICT[street_key] = [node for node in street if node in intersection_node_set]

    print("saving node dict...")
    pickle.dump(NODE_DICT, open(path + "maps\\{}.node_dict".format(placename), "wb"))

    print("saving polygon nodes...")
    pickle.dump(POLYGON_NODES, open(path + "maps\\{}.polygon_nodes".format(placename), "wb"))

    print("saving polygon tags...")
    pickle.dump(POLYGON_TAGS, open(path + "maps\\{}.polygon_tags".format(placename), "wb"))

    print("saving intersections...")
    pickle.dump(INTSEC_DICT, open(path + "maps\\{}.intsec_dict".format(placename), "wb"))

if __name__ == "__main__":
    parse_OSM(input("parse>"))
