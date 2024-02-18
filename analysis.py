import json
import xml.etree.ElementTree as ET

import numpy as np
from datasets import load_dataset, Split
from lxml import etree
from lxml.etree import _Element, _Attrib
import html
import openai


openai.base_url = "http://192.168.77.11:38000/v1/"
openai.api_key = "xxx"


def clear_attribs(node: _Element):
    keep_attribs = ['rowspan', 'colspan']
    keep_tags = ['table', 'tr', 'td', 'th', 'thead', 'tbody', 'tfoot', 'caption', 'colgroup', 'col']

    for attrib, value in node.attrib.items():
        if attrib.lower() not in keep_attribs or value == 1 or value == "1":
            node.attrib.pop(attrib)


def clear_table_content(content: str):
    content = html.unescape(content)

    for text in ["<bold>", "</bold>", "<italic>", "</italic>", "\r", "\n", "\t"]:
        content = content.replace(text, "")

    return content


def article_to_string(content: str):
    root: _Element = etree.fromstring(content)

    abstract = root.xpath("./front//abstract")[0]
    abstract_content = "\n".join(abstract.xpath(".//text()"))

    table_nodes = root.xpath("./body//table")
    for table_node in table_nodes:
        for node in table_node.iter():
            clear_attribs(node)

    parent_map = {c: p for p in root.iter() for c in p}

    table_nodes = root.xpath("./body//table")
    for table_node in table_nodes:
        parent = parent_map[table_node]

        newnode = etree.Element('table')
        newnode.text = clear_table_content(ET.tostring(table_node).decode(encoding='utf-8'))

        parent.replace(table_node, newnode)

    pnodes = root.xpath("./body//p")
    for pnode in pnodes:
        parent = parent_map[pnode]
        pcontent = "".join(pnode.xpath(".//text()"))

        newnode = etree.Element('p')
        newnode.text = pcontent

        parent.replace(pnode, newnode)

    content = "\n".join(root.xpath("./body//text()"))
    return abstract_content, content


def get_positions(text: str, anchor: str, window: int):
    positions = []
    text_len = len(text)
    anchor_len = len(anchor)

    offset = 0
    while offset < text_len - 1:
        try:
            pos = text.index(anchor, offset)
            if pos >= offset:
                positions.append([max(0, pos - window), min(text_len, pos + anchor_len + window)])
                offset = pos + anchor_len
            else:
                break
        except:
            break

    return positions


def merge_positions(positions: list):
    for idx0 in range(len(positions)):
        pos0 = positions[idx0]
        for idx1 in range(len(positions)):
            if idx0 == idx1:
                continue

            pos1 = positions[idx1]

            if pos0[0] <= pos1[0] <= pos0[1]:
                pos1[0] = pos0[0]
                pos1[1] = max(pos0[1], pos1[1])
                pos0[1] = pos1[1]
            elif pos0[0] <= pos1[1] <= pos0[1]:
                pos1[1] = pos0[1]
                pos1[0] = min(pos0[0], pos1[0])
                pos0[0] = pos1[0]

    if len(positions) == 1:
        return positions

    positions = [f"{pos[0]},{pos[1]}" for pos in positions]
    positions = np.unique(positions)

    new_positions = []
    for pos in positions:
        pp = pos.split(',')
        new_positions.append([int(pp[0]), int(pp[1])])

    return new_positions

fp = open('data/pubmed_outcome.jsonl', 'w', encoding='utf-8')

dataset = load_dataset("Corran/Pubmed-OpenAccess-Commercial-Use", split=Split.TRAIN, streaming=True)
count = 0
for item in dataset:
    count += 1
print(count)

# for idx, item in enumerate(dataset):
#     print(idx)
#
#     try:
#         abstract, content = article_to_string(item['data'][0])
#         content = content.lower()
#
#         if not ("primary outcome" in content or "secondary outcome" in content):
#             continue
#
#         positions = []
#         positions.extend(get_positions(content, "primary outcome", 300))
#         positions.extend(get_positions(content, "secondary outcome", 300))
#         positions = merge_positions(positions)
#
#         texts = []
#         for pos in positions:
#             texts.append(content[pos[0]:pos[1]])
#         texts = "\n".join(texts)
#
#         response = openai.chat.completions.create(messages=[
#             {'role': 'system', 'content': 'As a senior medical research expert, please provide advice on the best approach to take in order to answer my question effectively.'},
#             {'role': 'user', 'content': f"""Context: {texts}\n\nAnalysis above pieces of medical article and point out what is the primary outcome and secondary outcome."""}
#         ], model='chatglm3-6b-32k')
#
#         answer = response.choices[0].message.content
#
#         fp.write(json.dumps({
#             'prompt': 'As a senior medical research expert, please provide advice on the best approach to take in order to answer my question effectively.',
#             'input': f"""I am working on a medical research project. Please help me to design a primary outcome and secondary outcome according to the following study summary:\n\n{abstract}""",
#             'output': answer
#         }) + "\n")
#         fp.flush()
#
#         print("OK")
#
#     except Exception as e:
#         pass