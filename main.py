import csv
import math
from jamdict import Jamdict
from KanjiGraph import KanjiGraph

class KanjiEntry:
  def __init__(self, row):
    self.kanji = row['literal']
    self.stroke_count = row['stroke_count']

class VocabEntry: 
  def __init__(self, idseq, text):
    self.idseq = idseq
    self.text = text
    self.kanji_content = [char for char in self.text if '一' <= char <= '龯']
    self.log_cost = 20.0

def load_data():
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


if __name__ == "__main__":
  jam, entries = load_data()
  load_frequency_data(entries)

  kanji_count = sum(1 for entry in entries if isinstance(entry, KanjiEntry))
  def debug_check_data(entries, kanji_count):
    print("verify kanji nodes:")
    for i in range(5):
      entry = entries[i]
      print(f"Kanji Node {i+1}: {entry.kanji}, Strokes: {entry.stroke_count}")

    print("verify vocab nodes:")
    checks = 0
    for entry in entries:
      if isinstance(entry, VocabEntry):
        if entry.log_cost<20.0:
          kanji_list = ", ".join(entry.kanji_content)[:3]+"..." if len(entry.kanji_content) > 3 else ", ".join(entry.kanji_content)
          freq_status = "LOW" if entry.log_cost > 10 else "HIGH"
          print(f" Word: {entry.text} Cost: {entry.log_cost:.4f}, Frequency Status: {freq_status}, Kanji: {kanji_list}")
          checks+=1
          if checks >= 20:
            break
    if checks == 0:
      print("No loaded frequency found")

  debug_check_data(entries, kanji_count)
  graph = KanjiGraph()
