from nodes import *

#all this shit needs to be done in numpy tbh
def length(vec):
    return ( vec[0]**2 + vec[1]**2 )**0.5
    
def dot(vec1, vec2):
    return vec1[0] * vec2[0] + vec1[1] * vec2[1]

MIN_ROUTE_CHANCE = 0.05
MAX_CAP = 200

# cosine similarity as cost
def cos_sim(node, neighbor, goal):
    n = node.get_pos()
    nn = neighbor.get_pos()
    gn = goal.get_pos()
    
    n_vec = (nn[0] - n[0], nn[1] - n[1])
    g_vec = (gn[0] - n[0], gn[1] - n[1])
    
    try: return max(MIN_ROUTE_CHANCE, dot(n_vec, g_vec) / ( length(n_vec) * length(g_vec) ))
    except: return MIN_ROUTE_CHANCE
    
def distance(node, neighbor):
    n = node.get_pos()
    nn = neighbor.get_pos()

    return length((nn[0] - n[0], nn[1] - n[1]))

# RUH algorithm, start and end are both Node classes
def ruh(OSMInterface, start, end):
    # do some wacky shit
    
    l = len( OSMInterface.get_unique_intersections() )
    
    values = {start.ref: [(1, 0)]}
    visited = []
    to_visit = [start]
    
    print("running algorithm...")
    while to_visit != []:
        print( int(100*len(visited)/l) )
        current_node = to_visit[0]
        
        if len(set(visited)) != len(visited):
            print("help")
            input()
        
        for node in to_visit:
            if values[node.ref][0][0] > values[current_node.ref][0][0]:
                current_node = node
                
        visited.append( current_node.ref )
        
        neighbors = OSMInterface.get_neighbors( current_node )
        
        evidence = sum( [cos_sim(current_node, neighbor, end) for neighbor in neighbors] )
        
        for neighbor in neighbors:
            c = cos_sim(current_node, neighbor, end)/evidence
            
            if neighbor.ref not in values.keys():
                values[neighbor.ref] = [(pair[0] * c, pair[1] + distance(current_node, neighbor)) for pair in values[current_node.ref]]
                values[neighbor.ref] = sorted(values[neighbor.ref], key=lambda x: x[0])[:MAX_CAP]
                
            else: 
                values[neighbor.ref] += [(pair[0] * c, pair[1] + distance(current_node, neighbor)) for pair in values[current_node.ref]]
                values[neighbor.ref] = sorted(values[neighbor.ref], key=lambda x: x[0])[:MAX_CAP]
            
            if neighbor.ref not in visited:
            
                to_visit.append(neighbor)
                
        while current_node in to_visit: to_visit.remove( current_node )
                
    print("parsing...")
    
    print( values[end.ref] )
    
    for id, value_l in values.items():
        p = 0
        for pair in value_l:
            try: p += pair[0]/pair[1]
            except: pass
                
        values[id] = p
    
    print("done")
            
    return values
