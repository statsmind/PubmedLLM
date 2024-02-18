import json
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


if __name__ == "__main__":
    outfile = open(r"z:\datasets\gushicimingju.jsonl", "a", encoding="utf-8")

    for dirpath, dirnames, filenames in os.walk(r"Z:\datasets\www.gushicimingju.com"):
        for filename in filenames:
            if not filename.endswith(".html") or filename == "index.html":
                continue

            filename = os.path.join(dirpath, filename)
            with open(filename, "r", encoding="utf8") as fp:
                html = fp.read()

            print(filename)

            root = etree.HTML(html)
            nodes = root.xpath(".//*[@class='main-content gushi-info']")
            if len(nodes) < 2:
                continue

            texts = [etree.tostring(node, method='text', encoding="utf8").decode("utf8") for node in nodes]
            content = "\n".join(texts[:-1])
            content = strQ2B(content).replace("　", "").replace(" ", "")
            content = "\n".join([line.strip() for line in content.split("\n")])
            content = content.replace('', '').replace(' ', ' ')
            content = re.sub("[ ]+", " ", content)
            content = re.sub("\n+", "\n", content).strip()

            if len(content) > 150:
                outfile.write(json.dumps({
                    'text': content
                }, ensure_ascii=False) + "\n")