# DSA Kanji Graph

A tool for visualizing paths between kanji and vocabulary entries in the Japanese language. 

## Features:
- ~200k node graph of language elements gathered from JMDict, including kanji and vocabulary words.
- Edges assigned by kanji and vocabulary frequency data gathered online under fair use
  - (https://www.researchgate.net/publication/357159664_2242_Kanji_Frequency_List_ver_11 | https://tsukubawebcorpus.jp/en/)
- Implementation of Dijkstra's Algorithm, Bellman-Ford Algorithm, and BFS for graph traversal.
- Shows a comparison of the lexical routes found by these algorithms. Dijkstra's/Bellman-Ford will return a least-cost path representing the highest frequency/priority entries on the path to the target, which can be modelled as a 'learning path' to the analyzed word. BFS produces a fewest step route to the target, which can provide interesting entries or steps.

## Install:
- Clone source
- Run `pip install -r requirements.txt` in a python virtual environment
- Download 'frequency_data.csv' and 'kanji_frequency.csv' from the releases page and place them into the source folder.
- Application is run from main.py: `python main.py`

### Required:
Python 3.12 works on my machine (not 3.13) but in theory 3.10 or higher. 

