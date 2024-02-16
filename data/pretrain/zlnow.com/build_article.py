import json
import multiprocessing
import os.path
import re
import sys

from lxml import etree
from lxml.etree import _Element

from six import unichr

from data.pretrain.utils import output_article


def process_html_file(filename):
    jsonname = filename + ".json"
    if os.path.exists(jsonname):
        return

    try:
        with open(filename, "r", encoding="utf8") as fp:
            html = fp.read()
    except:
        return

    print(filename)

    root = etree.HTML(html)
    title = root.find(".//*[@id='h1title']")
    if title is None:
        return

    title = title.text.replace('', '').replace(' ', '')

    content = root.find(".//*[@id='endText']")
    if content is None:
        return

    # content = "\n".join(content.xpath(".//text()"))
    content = etree.tostring(content, method="text", encoding="utf8").decode("utf8")
    content = content.replace("　", "").replace(" ", "")
    content = "\n".join([line.strip() for line in content.split("\n")])
    content = content.replace('', '').replace(' ', ' ')
    content = re.sub("[ ]+", " ", content)
    content = re.sub("\n+", "\n", content).strip()

    english_content = re.sub("[^a-zA-Z]+", "", content)
    if len(english_content) * 7 > len(content):
        return

    if len(content) <= 150:
        return

    with open(jsonname, "w", encoding="utf8") as fp:
        fp.write(json.dumps({
            'title': title,
            'content': content,
        }, ensure_ascii=False) + "\n")


def process_file(filepath):
    try:
        with open(filepath, 'r', encoding='utf8') as fp:
            data = json.loads(fp.read())

        title, result = output_article("zlnow", data['title'], data['content'])
        print(title, result)
    except Exception as ex:
        print(ex)


if __name__ == "__main__":
    abs_filenames = []
    for dirpath, dirnames, filenames in os.walk(r"Z:\datasets\www.zlnow.com"):
        for filename in filenames:
            if not filename.endswith(".json"):
                continue

            filepath = os.path.join(dirpath, filename)
            abs_filenames.append(filepath)

    pool = multiprocessing.Pool(20)
    pool.map(process_file, abs_filenames)

    # for dirpath, dirnames, filenames in os.walk(r"Z:\datasets\www.zlnow.com"):
    #     for filename in filenames:
    #         if not filename.endswith(".json"):
    #             continue
    #
    #         filepath = os.path.join(dirpath, filename)
    #
    #         with open(os.path.join(dirpath, filename), 'r', encoding='utf8') as fp:
    #             data = json.loads(fp.read())
    #
    #         title, result = output_article("zlnow", data['title'], data['content'])
    #         print(title, result)
