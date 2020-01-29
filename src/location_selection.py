from nodes import *
import numpy as np

#OSMInterface = OSMInterfaceOBJ()
#OSMInterface.load_location("Bremm", origin = (7.0975, 50.1089) )

#print( 5955007897 in OSMInterface.WAY_INFO[ OSMInterface.current_location ].keys() )

#sizes of area in squared km
A = {}
B = {}
C = {}
# F["area"] = ("between", [10,15])
# F["area"] = ("greaterthan", 0.00000707)  # kleine auto
# F["area"] = ("greaterthan", 0.00001053)  # middel auto
# F["area"] = ("greaterthan", 0.00001203)  # grote auto
# F["area"] = ("greaterthan", 0.00001243)  # groot busje
# F["area"] = ("greaterthan", 0.00002125)  # kleine vrachtwagen
# F["area"] = ("greaterthan", 0.00004781)  # normale vrachtwagen
A["area"] = ("greaterthan", 0.00000135)  # fiets
# F["area"] = ("greaterthan", 0.0000005)   # personen drone
# A["area"] = ("greaterthan", 0.00005115)  # militaire drone
A["bruhhhhhhhhhhhhhhhhhhhhh"] = ["highway", "railway", "waterway", "natural"]

# F["area"] = ("greaterthan", 0.00003047)  # bus
# F["area"] = ("greaterthan", 0.00003022)  # buk
B["area"] = ("greaterthan", 0.00001147)  # hhmmmmv
# F["area"] = ("greaterthan", 0.00001537)  # hmmmv met mmr
# F["area"] = ("greaterthan", 0.00002132)  # kleine tank
# F["area"] = ("greaterthan", 0.00003587)  # grote tank
# F["area"] = ("greaterthan", 0.00002100)  # raket systeem
# F["area"] = ("greaterthan", 0)  # alle polygons

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

#m = 654706368
#p = 527798548
#print(OSMInterface.get_node_from_id(p).lat, OSMInterface.get_node_from_id(p).lon)
#print(o)
#print( area( o ) )

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

    if "bruhhhhhhhhhhhhhhhhhhhhh" in features.keys():
        f = False
        for ffff in features[ "bruhhhhhhhhhhhhhhhhhhhhh" ]:
            if ffff in OSMInterface.WAY_INFO[ OSMInterface.current_location ][way_id].keys():
                f = True
        if not f: return False

    return True

#a = [i[0] for i in query(OSMInterface, A)]
#print( len( a ) )
