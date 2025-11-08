import csv
import math
import random
from jamdict import Jamdict
from KanjiGraph import KanjiGraph

# Entry Type Objects
class KanjiEntry:
  def __init__(self, row):
    self.kanji = row['literal']
    self.stroke_count = row['stroke_count']
    self.log_cost = 20.0
    self.freq_rank = None

class VocabEntry: 
  def __init__(self, idseq, text):
    self.idseq = idseq
    self.text = text
    self.kanji_content = [char for char in self.text if '一' <= char <= '龯']
    self.log_cost = 20.0

# Data Loading Helper Functions
def load_data():
  print("-------------------LOADING DATA FOR GRAPH ANALYSIS---------------------")
  print("Loading initial Kanji Dictionary Data...")
  jam = Jamdict()
  entries = []

  # KANJI
  rows = jam.kd2.ctx().select("SELECT * FROM character")
  for row in rows:
    if row['literal'] and row['stroke_count'] is not None:
      entry = KanjiEntry(row)
      entries.append(entry)

  # VOCAB
  print("Loading Vocabulary data...")
  query = """
  SELECT T1.idseq, T2.text
  FROM Entry AS T1
  INNER JOIN Kanji AS T2 ON T1.idseq = T2.idseq;
  """
  vocab_rows = jam.jmdict.ctx().select(query)
  for row in vocab_rows:
    entries.append(VocabEntry(row['idseq'], row['text']))

  
  print(f"Loaded {len(entries)} entries from JMDict!")
  return jam, entries

def load_frequency_data(entries, filename='frequency_data.csv'):
  print("Loading corpus data from csv...")
  frequency_map = {}
  minimum_frequency = 1e-8
  MAX_COST = -math.log(minimum_frequency)
  try:
    with open(filename, mode='r', encoding='cp932') as f:
      reader = csv.reader(f)
      for row in reader:
        if len(row) >= 2:
          word_text = row[0].strip()
          try:
            norm_freq = float(row[1])
            bounded_freq = max(norm_freq, minimum_frequency)
            log_cost = -math.log(bounded_freq)
            frequency_map[word_text] = log_cost
          except (ValueError, IndexError):
            continue
  except FileNotFoundError:
    print("Error: could not find frequency file 'frequency_data.csv'. A default cost will be used for all vocabulary.")
    return
  matched = 0
  for entry in entries:
    if isinstance(entry, VocabEntry):
      if entry.kanji_content:
        entry.log_cost = frequency_map.get(entry.text, MAX_COST)
        if entry.log_cost < MAX_COST:
          matched += 1
  print("Frequency data loaded successfully!")

def load_kanji_frequency(entries, filename: str = "kanji_frequency.csv"):
  #LOADING
  kanji_rank_map = {}
  try:
    with open(filename, mode='r', encoding='cp932') as f:
      reader = csv.DictReader(f)
      for row in reader:
        kanji = row.get('FORM', '').strip()
        rank_str = row.get("FREQ (1)", '').strip()
        try:
          rank = float(rank_str)
          kanji_rank_map[kanji] = rank
        except ValueError:
          continue
  except FileNotFoundError:
    print(f"Kanji frequency file {filename} not found. Using default cost for kanji entries.")
    return
  if not kanji_rank_map:
    print("Kanji frequency data loaded successfully but the map is empty. Cost not calculated.")
    return
  min_rank = min(kanji_rank_map.values())
  matched = 0
  for entry in entries:
    if isinstance(entry, KanjiEntry):
      if entry.kanji in kanji_rank_map:
        rank = kanji_rank_map[entry.kanji]
        cost = math.log(rank / (min_rank +1e-9)) #+1e-9 was a way to prevent division by zero.
        entry.log_cost = max(cost, 0.1)
        entry.freq_rank = rank
        matched += 1
  print(f"Loaded frequency costs for {matched} kanji entries.")

  
# Populate Graph Helper Function
def build_graph(jam, graph, entries):
  print("Populating graph with loaded entries...")
  kanji_nodes = {}

  #Nodes
  for entry in entries:
    node_id = entry.kanji if isinstance(entry, KanjiEntry) else entry.text
    node_data = {"type": "kanji" if isinstance(entry, KanjiEntry) else 'vocab'}
    if isinstance(entry, KanjiEntry):
      kanji_nodes[entry.kanji] = entry
      node_data['entry_ref'] = entry
    graph.add_node(node_id, **node_data)
  print(f"Added {graph.node_count} nodes to graph.")

  #lexical edges
  print("Creating edges and assigning weights by frequency...")
  MAX_COST = 18.42
  RADICAL_COST = 25.0
  for entry in entries:
    if isinstance(entry, VocabEntry) and entry.kanji_content:
      word_node = entry.text
      word_cost = entry.log_cost
      for kanji_char in entry.kanji_content:
        kanji_ref = graph.nodes_data.get(kanji_char, {}).get('entry_ref')
        if kanji_ref and kanji_ref.log_cost < 20.0:
          kanji_cost = kanji_ref.log_cost
        else:
          kanji_cost = word_cost
        if kanji_char in graph.graph:
          # add word to kanji edge
          graph.add_edge(word_node, kanji_char, kanji_cost)
          #add kanji to word edge
          graph.add_edge(kanji_char, word_node, word_cost)

  #radical/decompisition nodes:
  for kanji in kanji_nodes.keys():
    components = jam.krad.get(kanji, [])
    for component in components:
      if component not in graph.graph:
        graph.add_node(component, type='radical')

      graph.add_edge(kanji, component, RADICAL_COST)
      graph.add_edge(component, kanji, RADICAL_COST)

  print(f"Edges created. Nodes used: {len(graph.graph)}")
  return graph

#helper function for printing formatted paths
def print_result(algo, result, graph):
  print('\n')
  print("-" * 60)
  print(f"RESULT FROM {algo}:")
  print("-" * 60)
  if result:
    if len(result) == 3: #bfs
      path, steps, cost = result
      cost_label = f"(Steps: {steps}, Total Weight: {cost:.4f})"
    else:
      path, cost = result
      cost_label = f"Total Weight: {cost:.4f}"
    formatted = graph.format_path(path)
    print(f"Path Located: {cost_label}\n")
    print("Sequence:")
    print(" --> ".join(formatted))
  else:
    print("Path not found! (Source node not found in the graph or is unreachable?)")

if __name__ == "__main__":
  jam, entries = load_data()
  load_frequency_data(entries)
  load_kanji_frequency(entries)
  empty_graph = KanjiGraph()
  graph = build_graph(jam, empty_graph, entries)
  N5_KANJI_SET = {
    '一', '二', '三', '四', '五', '六', '七', '八', '九', '十', '百', '千', '万', '円', '時', 
    '日', '月', '火', '水', '木', '金', '土', '曜', '本', '人', '今', '寺', '上', '下', '中', 
    '大', '小', '先', '入', '出', '山', '川', '田', '左', '右', '名', '語', '学', '生', '校', 
    '男', '女', '子', '車', '前', '後', '午', '分', '半', '何', '食', '飲', '駅', '休', '電', 
    '書', '聞', '読', '見', '話', '買', '行', '来', '出', '会', '口', '目', '耳', '手', '足', 
    '力', '気', '雨', '花', '草', '虫', '犬', '魚', '貝', '林', '森', '空', '立', '座', '言', 
    '道', '会', '母', '父', '友', '白', '赤', '青', '色', '好', '新', '古', '長', '多', '少',
    '早', '広', '高', '安', '安', '外', '国', '京', '都', '社', '店' 
} #this is used as a general target, as it is a set of kanji deemed to be the most basic, simple, and common in the language.
  print("---------------------------LOADING COMPLETE-----------------------------")

  #DETERMINE SOURCE
  user = input("\nPlease enter a Japanese kanji or word to analyze (ex. 鉱業) Leave blank for a random entry: ").strip()
  source = None
  if not user:
    valid_nodes = [node for node, data in graph.nodes_data.items() if data.get('type') == 'vocab' and graph.graph.get(node) and len(graph.graph.get(node)) > 0]
    if valid_nodes:
      source = random.choice(valid_nodes)
      print(f"Selected random vocabulary entry: {source}")
    else:
      print("failed to find valid nodes for random selection. exiting")
      exit()
  elif user in graph.graph:
    source = user
  else:
    print(f"Source provided ({user}) not found in graph / is an invalid entry. Exiting ")
    exit()

  #DETERMINE TARGET
  user_target = input (f"\nEnter a target kanji to be reached from the source (Leave blank to search for all {len(N5_KANJI_SET)} N5 Kanji): ").strip()
  if user_target and user_target in graph.graph:
    target = {user_target}
    print(f"Target Set: ({user_target})")
  elif user_target and user_target not in graph.graph:
    print(f"Target {user_target} not found in graph / is an invalid entry. Defaulting to N5 set.")
    target = N5_KANJI_SET
  else:
    print("Target Set: N5 Kanji Set")
    target = N5_KANJI_SET


  dijkstras_result = graph.dijkstras(source, target)
  print_result("Dijkstra's (Minimum Cost by Frequency)", dijkstras_result, graph)

  bellman_result = graph.bellman(source, target)
  print_result("Bellman-Ford (Minimum Cost by Frequency)", dijkstras_result, graph)

  bfs_result = graph.bfs(source, target)
  print_result("BFS (Minimum Steps to Target Set)", bfs_result, graph)



