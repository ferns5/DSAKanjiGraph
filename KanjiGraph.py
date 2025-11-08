import heapq #just a min heap implementation used for dijkstra's! the logic is still my own.
from typing import Dict, List, Optional, Tuple, Set # for dijkstras (made it easier to return None)
class KanjiGraph:
  #grpah building
  def __init__(self):
    self.graph = {}
    self.nodes_data = {}
    self.node_count = 0

  def add_node(self, node_id, **kwargs):
    if node_id not in self.graph:
      self.graph[node_id] = {}
      self.nodes_data[node_id] = kwargs
      self.node_count+=1

  def add_edge(self, source, target, weight):
    if source in self.graph and target in self.graph:
      self.graph[source][target] = weight

  #PATHFINDING
  def dijkstras(self, src, target_set: Set[str]) -> Optional[Tuple[List[str], float]]:
    if src not in self.graph:
      return None
    
    final_node = None
    min_target = float('inf')
    shortest = {node: float('inf') for node in self.graph}
    shortest[src] = 0.0
    heap = [[0.0, src]]
    pred_map: Dict[str, Optional[str]] = {node: None for node in self.graph}
    
    while heap: #while heap is not empty
      distance, node = heapq.heappop(heap)
      if distance > shortest[node]:
        continue
      if node in target_set:
        if distance < min_target:
          min_target = distance
          final_node = node
      #relax neighbors
      for path, weight in self.graph[node].items():
        total = distance + weight
        if total < shortest[path]:
          shortest[path] = total
          pred_map[path] = node
          heapq.heappush(heap, (total, path))
    #heap is empty
    if final_node is None:
      return None
    final_path = []
    n = final_node
    while n is not None:
      final_path.append(n)
      n = pred_map[n]
    final_path.reverse()
    return final_path, min_target

  def bellman(self, src, target_set: Set[str]) -> Optional[Tuple[List[str], float]]:
    if src not in self.graph:
      return None
    shortest = {node: float('inf') for node in self.graph}
    shortest[src] = 0.0
    pred_map: Dict[str, Optional[str]] = {node: None for node in self.graph}
    v = len(self.graph)

    #relaxtion iterations
    for i in range(v-1):
      updated = False
      for n1 in self.graph:
        for n2, weight in self.graph[n1].items():
          if shortest[n1] != float('inf') and shortest[n1] + weight < shortest[n2]:
            shortest[n2] = shortest[n1] + weight
            pred_map[n2] = n1
            updated = True
      if not updated:
        break

    #pathfind
    min_target = float('inf')
    final_node = None
    for node in target_set:
      if shortest.get(node, float('inf')) < min_target:
        min_target = shortest[node]
        final_node = node

    if final_node is None or min_target == float('inf'):
      return None
    final_path = []
    cur = final_node
    while cur is not None:
      final_path.append(cur)
      cur = pred_map[cur]
    final_path.reverse()
    return final_path, min_target

    
