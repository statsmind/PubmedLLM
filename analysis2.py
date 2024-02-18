import json
import xml.etree.ElementTree as ET

import numpy as np
from datasets import load_dataset, Split, DownloadMode, DownloadConfig
from lxml import etree
from lxml.etree import _Element, _Attrib
import html
import openai
from bs4 import BeautifulSoup
import unidecode


def get_max_content(nodes):
    node_contents = []
    for node in nodes:
        soup = BeautifulSoup(etree.tostring(node, encoding='utf-8').decode('utf-8'), features="lxml")
        node_contents.append(soup.get_text('\n'))

    if len(node_contents) == 0:
        return ""

    node_contents = sorted(node_contents, key=lambda x: len(x), reverse=True)
    return node_contents[0]


def process_article(content: str, dump_xml=False):
    raw_content = content
    content = content.replace('<break/>', '<p/>')
    content = content.replace('</sup>', ' </sup>')
    content = content.replace('</sub>', ' </sub>')

    try:
        root: _Element = etree.fromstring(content)
    except:
        root: _Element = etree.XML(content.encode())

    etree.strip_tags(root, 'bold', 'italic', 'xref', 'ext-link', 'sup', 'sub', 'span', 'a', 'caption', 'styled-content', 'uri')
    etree.strip_attributes(root, 'valign', 'align', 'style', 'frame', 'rules', 'position',
                           'border', 'rowspace', 'colspace', 'width', 'height', 'hspace', 'vspace',
                           'xmlns:xlink', 'xmlns:mml', 'xmlns')

    for tag in ['tr', 'th', 'td']:
        for tag_node in root.xpath(f'.//{tag}'):
            for attrib in ['colspan', 'rowspan']:
                attrib_value = tag_node.attrib.get(attrib)
                if attrib_value in [1, "1"]:
                    etree.strip_attributes(tag_node, attrib)

    for node in root.xpath("./back"):
        root.remove(node)

    node_map = {c: p for p in root.iter() for c in p}
    nodes = list(node_map.keys())

    excluded_tags = ['journal-id', 'journal-title-group', 'contrib-group', 'aff', 'author-notes', 'history',
                     'permissions', 'ack', 'ref-list', 'graphic', 'funding-group', 'counts']
    for node, pnode in node_map.items():
        if pnode not in nodes:
            continue

        if node.tag in excluded_tags:
            pnode: _Element = pnode
            pnode.remove(node)
            nodes.remove(node)

    pmc_id = root.xpath('./front/article-meta/article-id[@pub-id-type="pmc"]/text()')
    if len(pmc_id) == 0:
        raise ValueError("no pmc id")
    pmc_id = pmc_id[0]

    title = get_max_content(root.xpath('./front/article-meta/title-group/article-title'))
    abstract_content = get_max_content(root.xpath('./front/article-meta/abstract'))

    # 在输出成内容前需要对table进行额外的处理
    while True:
        detected_inner_table = False
        for table_node in root.xpath('.//table'):
            # 嵌套表格先处理内部的
            if len(table_node.xpath('.//table')) > 0:
                detected_inner_table = True
                continue

            table_node.attrib.clear()

            table_text_node = etree.Element("p")
            table_text_node.text = ET.tostring(table_node).decode('utf-8')

            p_node: _Element = node_map[table_node]
            p_node.replace(table_node, table_text_node)

            node_map[table_text_node] = p_node
            nodes.append(table_text_node)
            nodes.remove(table_node)

        if not detected_inner_table:
            break

    body_content = get_max_content(root.xpath('./body'))

    if dump_xml:
        with open(f'samples/article-{pmc_id}-raw.xml', 'w', encoding='utf-8') as fp:
            fp.write(raw_content)

        with open(f'samples/article-{pmc_id}.xml', 'w', encoding='utf-8') as fp:
            fp.write(etree.tostring(root, encoding='utf-8').decode('utf-8'))

        with open(f'samples/article-{pmc_id}-abstract.txt', 'w', encoding='utf-8') as fp:
            fp.write(abstract_content)

        with open(f'samples/article-{pmc_id}-body.txt', 'w', encoding='utf-8') as fp:
            fp.write(body_content)

    return pmc_id, title, abstract_content, body_content


# with open('samples/error_article.xml', 'r', encoding='utf-8') as fp:
#     process_article(fp.read(), True)
#
openai.base_url = "http://192.168.77.11:38000/v1/"
openai.api_key = "xxx"

download_config = DownloadConfig(local_files_only=True)
dataset = load_dataset("Corran/Pubmed-OpenAccess-Commercial-Use", split=Split.TRAIN, streaming=True,
                       download_mode=DownloadMode.REUSE_DATASET_IF_EXISTS,
                       download_config=download_config)
for idx, item in enumerate(dataset):
    # if idx >= 10:
    #     break
    pmc_id, title, abstract_content, body_content = process_article(item['data'][0], dump_xml=True)

    if len(title) == 0 or len(abstract_content) == 0 or len(body_content) == 0:
        print("found error")

    print(idx, len(title), len(abstract_content), len(body_content))

    response = openai.chat.completions.create(messages=[
        {'role': 'system',
         'content': f"""As a senior medical research expert, please read following medical article and provide advice on the best approach to take in order to answer my question effectively.
--------------------------------
{body_content}
"""},
        {'role': 'user',
         'content': f"""Please provide the information about the primary outcome and secondary outcome in the medical article, including the possible outcomes, the statistics method to support, the factors that should be considered in the statistics, the SAS program to run statistics. Use English to answer, and reply in JSON format with keys: "primary_outcome", "secondary_outcome", "possible_outcome", "statistics_method", "factors", "sas_program."""}
    ], model='chatglm3-6b-32k')

    answer = response.choices[0].message.content
    print(answer)
    print()
