from jamdict import Jamdict

try:
  jam = Jamdict()
except Exception as e:
  print("Couldn't load dictionary database, ensure jamdict-data is installed (pip install jamdict-data)")
  print(f"Details: {e}")
  exit()

query = "いぬ"
print(f"Querying db for {query}")
result = jam.lookup(query)

# JMDict Entries
if not result.entries:
  print("No entry found!")
else:
  print("\nDictionary Entries (JMDict):")
  for entry in result.entries:
    print(f"\nEntry: {entry.kanji_forms} / {entry.kana_forms}")

# Kanjidic character details
if not result.chars:
  print("\nNo character details found.")
else:
  print("\nKanji Details (Kanjidic):")
  for char in result.chars:
    print(f"\nKanji: {char.literal}")

print("----------End of Search------------")
