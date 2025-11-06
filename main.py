from jamdict import Jamdict
from KanjiGraph import KanjiGraph

class KanjiEntry:
  def __init__(self, row):
    self.kanji = row['literal']
    self.stroke_count = row['stroke_count']
    self.kanji_components = []

def load_data():
  print("Loading initial Japanese Dictionary Data...")
  jam = Jamdict()
  kanji_entries = []

  rows = jam.kd2.ctx().select("SELECT * FROM character")
  for row in rows:
    if row['literal'] and row['stroke_count'] is not None:
      kanji_entries.append(KanjiEntry(row))
  

  print(f"Loaded {len(kanji_entries)} entries from JMDict!")
  return jam, kanji_entries

if __name__ == "__main__":
  jam, kanji_entries = load_data()
  graph = KanjiGraph()
