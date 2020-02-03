from nodes import *
import numpy as np

def query(OSMInterface, features={}):

    all_ways = OSMInterface.get_streets()
    selected_ways = [way[0] for way_id, way in all_ways.items() if select(way_id, way, features, OSMInterface)] 
    
    return selected_ways

def area2(node_list):
    x_list = []
    y_list = []
    for n in node_list:
        n = OSMInterface.get_node_from_id(n)
        x_list.append(n.get_pos()[0])
        y_list.append(n.get_pos()[1])

    return 0.5 * np.abs(np.dot(x_list,np.roll(y_list,1))-np.dot(y_list,np.roll(x_list,1)))

def area3(corners):
    corners = PolygonSort(corners)
    n = len(corners)
    area = 0.0
    for i in range(n):
        j = (i + 1) % n
        area += corners[i][0] * corners[j][1]
        area -= corners[j][0] * corners[i][1]
    area = abs(area) / 2.0
    return area

def area(o):
    a = 0
    for i in range(len(o)):
        b = o[i]
        e = o[(i + 1)%len(o)]

        w = e[0] - b[0]
        h = (e[1] + b[1])/2

        a += w * h

    return abs(a)/0.34*1800/1000000

def select(way_id, way, features, OSMInterface):
    a = area( [OSMInterface.get_node_from_id(n).get_pos() for n in way] )
    if "area" in features.keys():
        relation = features["area"][0]
        if relation == "between":
            if not (features["area"][1][0] < a < features["area"][1][1]): return False
        elif relation == "lessthan":
            if a > features["area"][1]: return False
        elif relation == "greaterthan":
            if a < features["area"][1]: return False

    if "wanted_features" in features.keys():
        f = False
        for ffff in features[ "wanted_features" ]:
            if ffff in OSMInterface.WAY_INFO[way_id].keys():
                f = True
        if not f: return False

    return True
