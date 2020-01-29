from nodes import *
import copy
import algorithms.ruh
import algorithms.giraffe

# This is the Bayesian Rotationally Unidependent Heuristic Algorithm, aka the B.R.U.H. Algorithm.
# It takes a start and a goal, and gives every node in the network a set probability of passing through
# based solely on the rotation of the vector to the goal node
#
# The idea here is that we use Bayes' rule:
#
#                                                    P(Sighting given Goal) * P(Goal)
# P(Goal given a Sighting) =  ------------------------------------------------------------------------------
#                               P(Sighting given Goal) * P(Goal) + P(Sighting given not Goal) * P(not Goal)
#
# The idea is therefore that we assume a set of goals named goal_vector
# If no sightings have been made, their probabilities are uniform (or not, depends on location selection), like so:
# [ (Goal1, 33%), (Goal2, 33%), (Goal3, 33%) ]
#
# We then update this entire list with a sighting, so each probability becomes P(G | S)
# For example, we want to know the new probability of Goal 1, we have to calculate P(G1 | S)
# We know P(G1) = 0.33, P(G2) = 0.33, P(G3) = 0.33. After running dijkstra, we also know (for example) that
# If the thief went to G1, the chance they went past S is, say, 0.40. We also know that if the thief did not go to G1
# the chance they went past S is 0.1. We can then calculate the chance the thief went to G1 by using Bayes' rule.
# P(G1 | S) = P(S | G1)P(G1) / ( P(S | G1)P(G1) + P(S | not G1)P(not G1) )
# P(G1 | S) = 0.4*0.33 / (0.4*0.33 + 0.1*0.66) = 66%
# So now we know (Goal1, 66%)

#Bayesian RUH algorithm.
def bruh_update(OSMInterface, start, sighting, goal_vector, time=0, time_s=0.1, dist_s=20, features={}):
    new_vec = copy.deepcopy(goal_vector)
    
    # Get all the likelihoods to determine evidence
    likelihoods = {}
    for goal in goal_vector.keys():
        likelihoods[ goal ] = likelihood(OSMInterface, start, sighting, goal, time=time, time_s=time_s, dist_s=dist_s, features=features)
        
    # The evidence is     P(S | G)         *         P(G)            summed over all G
    evidence = sum( [ likelihoods[ goal] * goal_vector[ goal ] for goal in goal_vector.keys() ] )

    if evidence == 0:
        return goal_vector
    
    # update the goal_vector
    for goal in goal_vector.keys():
        new_vec[ goal ] = likelihoods[ goal ] * goal_vector[ goal ] / evidence
        
    return new_vec
    
def bruh(OSMInterface, start, goal_vector, max_speed=20, features={}, time=0, time_s=0.1, dist_s=20):
    v_dict = {}
    v_final = {}
    for goal in goal_vector.keys():
        g = OSMInterface.get_node_from_id( goal )
        p = algorithms.giraffe.giraffe(OSMInterface, start, g, time=time, time_s=time_s, dist_s=dist_s, features=features)
        v_dict[ goal ] = p
        
        for k, v in v_dict[ goal ].items():
            v_dict[ goal ][k] = v * goal_vector[ goal ]
            
    for g, d in v_dict.items():
        for node in d.keys():
            try: v_final[ node ] += d[ node ]
            except: v_final[ node ] = d[ node ]
            
    return v_final
    
def likelihood(OSMInterface, start, sighting, goal, time=0, time_s=0.1, dist_s=20, features={}): 
    # this is where you would run an algorithm that can determine probabilities of each and every node,
    goal = OSMInterface.get_node_from_id( goal )
    v = algorithms.giraffe.giraffe(OSMInterface, start, goal, time=time, time_s=time_s, dist_s=dist_s, features=features)
    
    # returns P(sighting | goal)
    if sighting.ref in v.keys(): return v[sighting.ref]
    else: return 0
