import json
import multiprocessing
import os
import zipfile
from lxml import etree

from data.pretrain.utils import output_article, base_path


def parse_html(filepath):
    print(filepath)
    with open(filepath, 'r', encoding='GB18030') as fp:
        root = etree.HTML(fp.read())
        first_table = root.find(".//table")
        title_nodes = first_table.xpath(".//td")
        title_text = [etree.tostring(node, method='text', encoding='utf-8').decode('utf-8') for node in title_nodes]
        if len(title_text) == 1:
            title = title_text[0]
        elif len(title_text) == 2:
            title = title_text[1] + ' ' + title_text[0]
        else:
            title = ""

        title = title.replace("《", "").replace("》", "")

        node = root.find(".//td[@valign=\"top\"]")

        for table in node.xpath(".//table"):
            table.getparent().remove(table)

        content = etree.tostring(node, method='text', encoding='utf-8').decode('utf-8')
        return title, content


def process_file(filepath):
    title, content = parse_html(filepath)
    try:
        title, result = output_article("zysj", title, content)
        print(title, result)
    except Exception as ex:
        print(ex)


if __name__ == '__main__':
    abs_filenames = []
    for dirpath, dirnames, filenames in os.walk(os.path.join(base_path, "www.zysj.com")):
        filenames = [filename for filename in filenames if filename.endswith(".htm") and filename != '00.htm']
        for filename in filenames:
            filepath = os.path.join(dirpath, filename)
            abs_filenames.append(filepath)

    print(len(abs_filenames))

    pool = multiprocessing.Pool(20)
    pool.map(process_file, abs_filenames)

    # for dirpath, dirnames, filenames in os.walk(r"Z:\datasets\www.zysj.com"):
    #     filenames = [filename for filename in filenames if filename.endswith(".htm") and filename != '00.htm']
    #     for filename in filenames:
    #         filepath = os.path.join(dirpath, filename)
    #         try:
    #             title, content = parse_html(filepath)
    #             title, result = output_article("zysj", title, content)
    #             print(title, result)
    #         except Exception as ex:
    #             print(ex)
