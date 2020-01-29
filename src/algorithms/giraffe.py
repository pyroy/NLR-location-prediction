from nodes import *
import math
import algorithms.astar
import copy

# speed is in km/u
def giraffe( OSMInterface, start_node, end_node, max_speed=20, features={}, time=0, time_s=0.1, dist_s=20 ):
    max_speed = features["max_speed"]
    max_speed *= 10
    path = algorithms.astar.astar( OSMInterface, start_node, end_node, max_speed=max_speed, retv=True, features=features )

    # if path is not accesible with given ways
    if path == [] or path is None:
        return {n.ref: 0 for n in OSMInterface.get_unique_intersections()}

    values = {p[0].ref: 0 for p in path}
    values2 = {p[0].ref: p[1] for p in path}

    to_visit = [p[0] for p in path]
    visited = []

    l = len( OSMInterface.get_unique_intersections() )

    while to_visit != []:
        to_visit_2 = []
        
        for node in to_visit:

            for neighbor in OSMInterface.get_neighbors( node ):
                if not OSMInterface.check_features(node, neighbor, features):
                    break

                try:
                    values[ neighbor.ref ] = min(values[ neighbor.ref ], values[ node.ref ] + OSMInterface.distance( node.get_pos(), neighbor.get_pos() )) #order matters for incline
                    values2[ neighbor.ref ] = min(values2[ neighbor.ref ], values2[ node.ref ] + OSMInterface.get_time_between( node, neighbor, speed=max_speed ))
                except:
                    values[ neighbor.ref ] = values[ node.ref ] + OSMInterface.distance( node.get_pos(), neighbor.get_pos() )
                    values2[ neighbor.ref ] = values2[ node.ref ] + OSMInterface.get_time_between( node, neighbor, speed=max_speed )

                if (neighbor not in visited) and (neighbor not in to_visit_2):
                    to_visit_2.append( neighbor )

        visited += copy.copy(to_visit)
        to_visit = copy.copy(to_visit_2)

        for n in visited:
            if n in to_visit:
                to_visit.remove(n)
    
    v2 = {n: math.exp( -((time - b)/time_s)**2 ) for n, b in values2.items()}

    v = {n: math.exp( -(b/dist_s)**2 ) for n, b in values.items()}
    
    for k in values2.keys():
        v[ k ] = v[ k ] * v2[ k ]

    return v
