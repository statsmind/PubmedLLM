import json
from typing import List

from datasets import load_dataset, Split


"""
Build datasets for sft stage


"""

mesh_fp = open('data/pubmed_mesh.jsonl', 'w', encoding='utf8')
qa_fp = open('data/pubmed_qa.jsonl', 'w', encoding='utf8')

dataset1 = load_dataset("bigbio/pubmed_qa", "pubmed_qa_artificial_source",
                        split=Split.ALL, trust_remote_code=True)
dataset2 = load_dataset("bigbio/pubmed_qa", "pubmed_qa_artificial_bigbio_qa",
                        split=Split.ALL, trust_remote_code=True)
dataset3 = load_dataset("bigbio/pubmed_qa", "pubmed_qa_unlabeled_source",
                        split=Split.ALL, trust_remote_code=True)
dataset4 = load_dataset("bigbio/pubmed_qa", "pubmed_qa_unlabeled_bigbio_qa",
                        split=Split.ALL, trust_remote_code=True)

for dataset in [zip(dataset1, dataset2), zip(dataset3, dataset4)]:
    for item in dataset:
        item = {**item[0], **item[1]}

        if len(item['MESHES']) > 0:
            mesh_fp.write(json.dumps({
                'pmid': item['document_id'],
                'prompt': 'Extract the MeSH terms from following text, return with JSON format.',
                'input': item['context'],
                'output': json.dumps(item['MESHES'])
            }) + "\n")

        if isinstance(item['answer'], List) and len(item['answer']) == 1:
            answer = item['answer'][0]
            if answer in ['yes', 'no', 'maybe']:
                answer = "\nSo the final answer is: {answer}"
            else:
                answer = ""

            qa_fp.write(json.dumps({
                'pmid': item['document_id'],
                'prompt': f"Read following text and answer my question..\n\n{item['context']}",
                'input': item['question'],
                'output': item['LONG_ANSWER'] + answer
            }) + "\n")

mesh_fp.close()
qa_fp.close()
