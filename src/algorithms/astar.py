# Algorithm lifted from unknown site
# Modified for use with our classes

from nodes import *

def astar(OSMInterface, start_node, end_node, max_speed=1, retv=False, features={}):
    max_speed = features["max_speed"]
    start_node.g = start_node.h = start_node.f = 0
    end_node.g = end_node.h = end_node.f = 0
    open_list = []
    closed_list = []
    open_list.append(start_node)

    while len(open_list) > 0:
        
        current_node = open_list[0]
        current_index = 0
        for index, item in enumerate(open_list):
            if item.f < current_node.f:
                current_node = item
                current_index = index
                
        open_list.pop(current_index)
        closed_list.append(current_node)

        # The code in this if loop is very wonky
        # And needs to be looked at, if we want to speed up the algorithm
        if current_node == end_node:
            path = []
            path_v = []
            current = current_node
            while current is not None and current not in path:
            
                if retv:
                    path_v.append( (current, current.g) )
                path.append( current )
                
                if current.parent == None: break
                
                current = OSMInterface.get_node_from_id( current.parent )
                
            if retv:
                return path_v[::-1]
                
            return path[::-1]

        children = OSMInterface.get_neighbors(current_node)

        for child in children:
            skip = False
            if not OSMInterface.check_features(child, current_node, features):
                skip = True
            for closed_child in closed_list:
                if child.ref == closed_child.ref:
                    skip = True
                    
            if not skip:
                d = OSMInterface.get_time_between( current_node, child, speed=max_speed )
                child.parent = current_node.ref
                child.g = current_node.g + d
                child.h = d
                child.f = child.g + child.h

                skip = False
                for open_node in open_list:
                    if child == open_node and child.g > open_node.g:
                        skip = True

                if not skip: open_list.append(child)
    return
