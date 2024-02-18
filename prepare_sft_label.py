import json
from datasets import load_dataset, Split
import numpy as np


dataset = load_dataset("ml4pubmed/pubmed-classification-20k", split=Split.ALL, trust_remote_code=True)

labels = [label for label in np.unique(dataset['label']) if not label.startswith('#')]
print(labels)

fp = open('data/pubmed_phrase_label.jsonl', 'w', encoding='utf8')

for item in dataset:
    if item['label'].startswith('#'):
        continue

    fp.write(json.dumps({
        "prompt": "Classify the following text to one of the following labels: OBJECTIVE, METHODS, CONCLUSIONS, BACKGROUND, RESULTS.",
        "input": item['text'],
        "output": item['label']
    }) + '\n')

fp.close()