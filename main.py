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
    self.frequency = 0.0

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

if __name__ == "__main__":
  jam, entries = load_data()
  
  def debug_check_data(entries, kanji_count=13108):
    print("verify kanji nodes:")
    for i in range(5):
      entry = entries[i]
      print(f"Kanji Node {i+1}: {entry.kanji}, Strokes: {entry.stroke_count}")

    print("verify vocab nodes:")
    for i in range(kanji_count, kanji_count+5):
      entry = entries[i]
      kanji_list = ", ".join(entry.kanji_content[:3]) + "..." if len(entry.kanji_content) > 3 else ", ".join(entry.kanji_content)
      print(f" Vocab Node {i - kanji_count + 1}: {entry.text}, ID: {entry.idseq}, Kanji Content: [{kanji_list}]")

  debug_check_data(entries)
  graph = KanjiGraph()
