import json
from datasets import load_dataset, Split

dataset = load_dataset("taln-ls2n/pubmed", split=Split.ALL, trust_remote_code=True)

fp = open('data/pubmed_keyphrase.jsonl', 'w', encoding='utf8')

for item in dataset:
    fp.write(json.dumps({
        "prompt": "Extract the keyphrases from following text, return with JSON format.",
        "input": item['text'],
        "output": json.dumps(item['keyphrases'])
    }) + '\n')

fp.close()