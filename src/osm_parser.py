import os
from xml.dom import minidom
import pickle
import sys
from nodes import Node

path = os.path.dirname(os.path.abspath(__file__)) + "\\"
path = path[:-4]

def get_node_data(node):
    t = node.getElementsByTagName("tag")
    retdict = {}
    for tag in t:
        key = tag.getAttribute("k")
        val = tag.getAttribute("v")
        retdict[key] = val
    return retdict

class OSM:
    def __init__(self):
        self.node_dict = {}
        self.street_dict = {}
        self.places = []
        self.places_named = []
        self.amenities = []
        self.fuel_stations = []
        self.post_boxes = []
        self.houses = []
        self.shops = []
        self.bus_stops = []
        self.streets = []
        self.streets_named = []
        self.parking = []
        self.way_dict = {}
        self.street_intersection_dict = {}
        self.polygon_list = []
        self.way_info = {}

def parse_OSM(placename):
    o = OSM()

    print("converting to DOM...")
    xml = minidom.parse(path+"maps\\{}.osm".format(placename))
    nodes = xml.getElementsByTagName('node')
    ways = xml.getElementsByTagName('way')
    relations = xml.getElementsByTagName('relation')

    print("parsing nodes...")

    for node in nodes:
        data = get_node_data( node )

        lat = float(node.getAttribute("lat"))
        lon = float(node.getAttribute("lon"))
        idn = int(node.getAttribute("id"))

        node = (idn, lat, lon)

        o.node_dict[ idn ] = Node(idn, lat, lon, data)
        
        if "place" in data.keys():
            o.places.append( node )
            o.places_named.append( data["name"] )

        elif "amenity" in data.keys():
            o.amenities.append( node )
            if data["amenity"] == "fuel":
                o.fuel_stations.append( node )
            elif data["amenity"] == "post_box":
                o.post_boxes.append( node )
            elif data["amenity"] == "parking":
                o.parking.append( node )

        elif "addr:housenumber" in data.keys():
            o.houses.append( node )

        elif "shop" in data.keys():
            o.shops.append( node )

        elif "highway" in data.keys() and data["highway"] == "bus_stop":
            o.bus_stops.append( node )

    print("parsing ways...")

    for way in ways:
        data = get_node_data( way )

        temp = []
        
        for node in way.getElementsByTagName("nd"):
            temp.append( int(node.getAttribute("ref")) )

        # some ways are buildings for some reason
        if "highway" in data.keys():
            o.street_dict[ int(way.getAttribute("id")) ] = temp
        o.way_dict[ int(way.getAttribute("id")) ] = temp
        o.way_info[ int(way.getAttribute("id")) ] = data
        
        o.streets.append( way )
        if "name" in data.keys():
            o.streets_named.append( data["name"] )

    print("creating node network...")
       
    intersection_node_set = []
    for street_key in o.street_dict.keys():
        intersection_node_set += [ node for node in o.street_dict[street_key] ]
        
    for node in list(set(intersection_node_set)):
        intersection_node_set.remove(node)
        
    intersection_node_set = list(set(intersection_node_set))
    
    for street_key in o.street_dict.keys():
        street = o.street_dict[street_key]
        o.street_intersection_dict[street_key] = [node for node in street if node in intersection_node_set]

    print("parsing relations...")

    for relation in relations:
        d = get_node_data( relation )
        if "type" in d.keys() and d["type"] == "multipolygon":
            o.polygon_list.append( [member.getAttribute("ref") for member in relation.getElementsByTagName("member") if member.getAttribute("role") == "outer"] )

    print("saving node dict...")
    pickle.dump(o.node_dict, open(path + "maps\\{}.node_info".format(placename), "wb"))

    print("saving street dict...")
    pickle.dump(o.way_dict, open(path + "maps\\{}.street_info".format(placename), "wb"))

    print("saving polygons...")
    pickle.dump(o.polygon_list, open(path + "maps\\{}.polygons".format(placename), "wb"))

    print("saving way info...")
    pickle.dump(o.way_info, open(path + "maps\\{}.additional".format(placename), "wb"))

    print("saving intersections...")
    pickle.dump(o.street_intersection_dict, open(path + "maps\\{}.intsec_info".format(placename), "wb"))

    return o

if __name__ == "__main__":
    o = parse_OSM(input("parse>"))
