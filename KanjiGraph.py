class KanjiGraph:
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
