import pickle, os, math

# PATH contains the path to root of the project assuming this file is
# located inside the /src/ folder
PATH = os.path.dirname(os.path.abspath(__file__)) + "\\"
PATH = PATH[:-4]

class Node:
    def __init__(self, ref, lat, lon, data):
        # These 4 values are set by the parser
        self.ref = ref
        self.lat = lat
        self.lon = lon
        self.data = data

        #These are calculated and adjusted when loading in the map
        self.x = None
        self.y = None
        self.attributes = list(data.keys())

        #These are used by the algorithms
        self.streets = []
        self.parent = None
        self.f = 0
        self.g = 0
        self.h = 0

    def get_lat_pos(self):
        return (float(self.lat), float(self.lon))
    
    def get_pos(self, offset = (0,0), scale = 1):
        return (scale*self.x + offset[0], scale*self.y + offset[1])
        
    def update_screen_position(self, pos):
        self.x = pos[0]
        self.y = pos[1]
        
    def has_attribute(self, attribute):
        return attribute in self.data.keys()
        
    def get_value(self, attribute):
        return self.data[attribute]

    def __eq__(self, other):
        return self.ref == other.ref

class OSMInterfaceOBJ:
    def __init__(self, location, origin=(0,0)):
        self.NODE_DICTS = pickle.load(open(PATH + "maps\\{}.node_dict".format(location), "rb"))
        self.STREET_DICTS = pickle.load(open(PATH + "maps\\{}.polygon_nodes".format(location), "rb"))
        self.INTSEC_DICTS = pickle.load(open(PATH + "maps\\{}.intsec_dict".format(location), "rb"))
        self.WAY_INFO = pickle.load(open(PATH + "maps\\{}.polygon_tags".format(location), "rb"))

        # This calculates the x, y position of the nodes relative to an origin
        for node_id, NodeOBJ in self.NODE_DICTS.items():
            NodeOBJ.update_screen_position( self.latlon_to_xy(NodeOBJ.lon, NodeOBJ.lat, origin) )
        
        unique_node_set = []
        for street_id, intersecting_nodes in self.get_intersections().items():
            for node_id in intersecting_nodes:
                unique_node_set.append( node_id )
        self.UNIQUE_INTERSECTING_NODES = [self.get_node_from_id(node_id) for node_id in list(set(unique_node_set))]

        # Code to detect origin coordinates
        
        lat_max = -100; lat_min = 100; lon_max = -100; lon_min = 100

        for Node in self.get_unique_intersections():
            
                p = Node.get_lat_pos()
                
                if p[0] > lat_max:
                    lat_max = p[0]
                elif p[0] < lat_min:
                    lat_min = p[0]
                if p[1] > lon_max:
                    lon_max = p[1]
                elif p[1] < lon_min:
                    lon_min = p[1]

        self.l_min = (lat_min, lon_min)
        self.l_max = (lat_max, lon_max)
        
    def latlon_to_xy(self, lat, long, origin):

        # in hectometer
        x_rel_to_origin = -(origin[0]-lat)*400000*math.cos((origin[0]+lat)*math.pi/360)/360
        y_rel_to_origin = (origin[1]-long)*400000/360
        
        return (x_rel_to_origin, y_rel_to_origin)
        
    def get_unique_intersections(self):
        return self.UNIQUE_INTERSECTING_NODES
        
    def get_streets(self):
        return self.STREET_DICTS
        
    def get_intersections(self):
        return self.INTSEC_DICTS
        
    def get_node_from_id(self, node_id):
        return self.NODE_DICTS[node_id]

    # returns true if the street between the two given nodes has the given features
    def check_features(self, b, e, features):
        s1 = self.get_streets_of_node(b)
        s2 = self.get_streets_of_node(e)
        
        st = None
        for street in s1:
            if street in s2:
                st = street
                break

        if st is None: return False
        data = self.WAY_INFO[ st ]

        if "wanted_features" in features.keys():
            for f in features["wanted_features"]:
                if f not in data.keys(): return False

        if "waytype" in features.keys():
            if "highway" not in data.keys(): return False
            else: return data["highway"] in features["waytype"]

        if "surfacetype" in features.keys():
            if "surface" not in data.keys(): return False
            else: return data["surface"] in features["surfacetype"]

        return True
        
    def get_nodes(self):
        return self.NODE_DICTS

    def get_incline(self, node1, node2):
        base = self.distance( node1.get_pos(), node2.get_pos() )
        try: height = float(node2.data["height"]) - float(node1.data["height"])
        except: 
            print(node2.data["height"], node1.data["height"]); return 0
            
        # returns in radians
        return math.atan(height/base)
    
    def get_streets_of_node(self, node):
        # TODO move this function to parser
        node_id = node.ref
        return [street_id for street_id, nodes_in_street in self.INTSEC_DICTS.items() if node_id in nodes_in_street]
        
    def distance(self, pos1, pos2):
        return math.sqrt( (pos1[0] - pos2[0])**2 + (pos1[1] - pos2[1])**2 )
        
    # speed is hm/u
    def get_time_between(self, node1, node2, speed=1):
        d = self.distance(node1.get_pos(), node2.get_pos())
        
        # incline in radians
        i = self.get_incline(node1, node2)
        
        #print("::", d / speed, math.cos( i ))
        
        if i >= 0:
            return d / speed / math.sqrt(math.cos( i )) #cosine goes to 0 as incline goes to 90 degrees
            
        if i < 0:
            return d / speed * math.sqrt(math.cos( i ))

    def get_way_info(self, way_id):
        return self.WAY_INFO[way_id]

    # closest node to a coordinate (x, y)
    def get_nearest_node_to(self, pos):
        best = None
        best_distance = 1000000
        
        for Node in self.get_unique_intersections():
                d = self.distance(pos, Node.get_pos())
                if d < best_distance:
                    best_distance = d
                    best = Node

        if best is None:
            print( "Something has gone wrong with the node coordinates." )
            
        return best

    # get node closest to a (lat, lon) coordinate, used to detect nodes inputted by the interface
    def get_nearestll(self, pos):
        best = None
        best_distance = 1000000
        
        for Node in self.get_unique_intersections():
                d = self.distance(pos, (Node.lat, Node.lon))
                if d < best_distance:
                    best_distance = d
                    best = Node

        if best is None:
            print( "Something has gone wrong with the node coordinates." )
            
        return best

    def get_int_from_node(self, node_id):
        return self.get_nearest_node_to( self.get_node_from_id( node_id ).get_pos() )
    
    def get_neighbors(self, node):
        ret_list = []
        for street_id in self.get_streets_of_node( node ):
            for i in range(len( self.get_intersections()[street_id] )):
                if self.get_intersections()[street_id][i] == node.ref:
                    if i > 0:
                        ret_list.append( self.get_node_from_id( self.get_intersections()[street_id][i-1] ) )
                    if i < len( self.get_intersections()[street_id] ) - 1:
                        ret_list.append( self.get_node_from_id( self.get_intersections()[street_id][i+1] ) )
        return [i for i in ret_list if i.ref != node.ref]
        
    #def get_k_nearest(self, node, k):
    #    node_streets = self.get_streets_of_node( node )
