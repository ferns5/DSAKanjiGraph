class KanjiGraph:
  def __init__(self):
    self.graph = {}
  def add_node(self, kanji: str):
    if kanji not in self.graph:
      self.graph[kanji] = {}
  def add_edge(self, source: str, target: str, weight: int):
    self.add_node(source)
    self.add_node(target)
    self.graph[source][target] = weight
