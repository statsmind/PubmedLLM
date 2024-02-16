import json
import multiprocessing
import os.path
import re
import sys

from lxml import etree
from lxml.etree import _Element

from six import unichr


def strQ2B(ustring):
    """全角转半角"""
    rstring = ""
    for uchar in ustring:
        inside_code = ord(uchar)
        if inside_code == 12288:  # 全角空格直接转换
            inside_code = 32
        elif (inside_code >= 65281 and inside_code <= 65374):  # 全角字符（除空格）根据关系转化
            inside_code -= 65248

        rstring += unichr(inside_code)
    return rstring


def split_text(text: str, window: int, overlap: int):
    text_len = len(text)
    if text_len <= window:
        yield text
        return

    steps = int(((text_len - overlap) + (window - overlap - 1)) / (window - overlap))
    for step in range(steps):
        start = min(text_len, step * (window - overlap))
        end = min(text_len, start + window)

        if end > start:
            piece = text[start:end]
            if len(piece) <= window / 4:
                piece = text[-window:]
            yield piece


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
    title = strQ2B(title.text)
    title = title.replace('', '').replace(' ', '')

    content = root.find(".//*[@id='endText']")
    if content is None:
        return

    # content = "\n".join(content.xpath(".//text()"))
    content = etree.tostring(content, method="text", encoding="utf8").decode("utf8")
    content = strQ2B(content).replace("　", "").replace(" ", "")
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


if __name__ == "__main__":
    # pool = multiprocessing.Pool(4)
    #
    # all_filenames = []
    # for dirpath, dirnames, filenames in os.walk("."):
    #     for filename in filenames:
    #         if not filename.endswith(".html"):
    #             continue
    #
    #         all_filenames.append(os.path.join(dirpath, filename))
    #
    # pool.map(process_html_file, all_filenames)

    outfile = open(r"Z:\datasets\zlnow.jsonl", "w", encoding="utf-8")
    for dirpath, dirnames, filenames in os.walk(r"Z:\datasets\www.zlnow.com"):
        for filename in filenames:
            if not filename.endswith(".json"):
                continue

            print(dirpath, filename)

            with open(os.path.join(dirpath, filename), 'r', encoding='utf8') as fp:
                data = json.loads(fp.read())

            outfile.write(json.dumps({
                'text': data['title'] + "\n" + data['content']
            }, ensure_ascii=False) + "\n")
            outfile.flush()
