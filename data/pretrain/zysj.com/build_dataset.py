import json
import multiprocessing
import os
import zipfile
from lxml import etree


def parse_html(filepath):
    print(filepath)
    with open(filepath, 'r', encoding='GB18030') as fp:
        root = etree.HTML(fp.read())
        node = root.find(".//td[@valign=\"top\"]")

        for table in node.xpath(".//table"):
            table.getparent().remove(table)

        content = etree.tostring(node, method='text', encoding='utf-8').decode('utf-8')
        return content

if __name__ == '__main__':
    abs_filenames = []
    for dirpath, dirnames, filenames in os.walk(r"Z:\datasets\www.zysj.com"):
        abs_filenames.extend([os.path.join(dirpath, filename)
                          for filename in filenames if filename.endswith(".htm") and filename != '00.htm'])

    pool = multiprocessing.Pool(10)
    with open(r"z:\datasets\zysj.jsonl", "w", encoding="utf-8") as out:
        for content in pool.map(parse_html, abs_filenames):
            out.write(json.dumps({
                'text': content
            }, ensure_ascii=False) + "\n")
        # filenames = [filename for filename in filenames if filename.endswith(".htm") and filename != '00.htm']
        # for filename in filenames:
        #     filepath = os.path.join(dirpath, filename)
        #     print(filepath)
        #     with open(filepath, 'r', encoding='GB18030') as fp:
        #         root = etree.HTML(fp.read())
        #         node = root.find(".//td[@valign=\"top\"]")
        #
        #         for table in node.xpath(".//table"):
        #             table.getparent().remove(table)
        #
        #         content = etree.tostring(node, method='text', encoding='utf-8').decode('utf-8')
        #         out.write(json.dumps({
        #             'text': content
        #         }, ensure_ascii=False) + "\n")
