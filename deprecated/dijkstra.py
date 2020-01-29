from nodes import *

def dijkstra(OSMInterface, nodes, initial, goal, max_t=1, speed=7):
  speed = speed * 3.6 * 3
  visited = {initial.ref: OSMInterface.distance(initial.get_pos(), goal.get_pos())}
  times = {initial.ref: 0}
  path = {}
  it = 0

  nodes = nodes

  while nodes:
    it += 1
    min_node = None
    for node in nodes:
      if node.ref in visited and times[node.ref] < max_t:
        if min_node is None:
          min_node = node
        elif visited[node.ref] < visited[min_node.ref]:
          min_node = node

    if min_node is None:
      print(it)
      break

    nodes.remove(min_node)
    current_weight = visited[min_node.ref]
    current_time = times[min_node.ref]

    for neighbor in OSMInterface.get_neighbors(min_node):
      weight = max(0, current_weight + OSMInterface.distance(neighbor.get_pos(), min_node.get_pos())*OSMInterface.distance(neighbor.get_pos(), goal.get_pos()))
      time = current_time + OSMInterface.distance(neighbor.get_pos(), min_node.get_pos())/speed
      if (neighbor.ref, min_node.ref) not in visited or weight < visited[(neighbor.ref, min_node.ref)]:
        visited[neighbor.ref] = weight
        times[neighbor.ref] = time
        path[neighbor.ref] = min_node.ref

  return times, visited, path
