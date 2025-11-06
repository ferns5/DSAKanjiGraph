from jamdict import Jamdict
from KanjiGraph import KanjiGraph

class KanjiEntry:
  def __init__(self, row):
    self.kanji = row['literal']
    self.stroke_count = row['stroke_count']
    self.kanji_components = []

class VocabEntry: 
  def __init__(self, idseq, text):
    self.idseq = idseq
    self.text = text
    self.kanji_content = [char for char in self.text if '一' <= char <= '龯']

def load_data():
  print("Loading initial Kanji Dictionary Data...")
  jam = Jamdict()
  entries = []

  # KANJI
  rows = jam.kd2.ctx().select("SELECT * FROM character")
  for row in rows:
    if row['literal'] and row['stroke_count'] is not None:
      entries.append(KanjiEntry(row))

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
  graph = KanjiGraph()
