import os
import platform
import re
from typing import Tuple

import zhconv
from six import unichr
from lxml import etree
import json


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


def html_to_text(html):
    try:
        root = etree.HTML(html)
        content = etree.tostring(root, method='text', encoding="utf8").decode("utf8")
        if content is None or len(content) == 0:
            return html
        else:
            return content
    except:
        return html


space_patten = re.compile(r'([\u4e00-\u9fa5])\s+([\u4e00-\u9fa5])')

if platform.system() == "Windows":
    base_path = r"z:\datasets"
else:
    base_path = "/nfs/datasets"


def format_text(text, is_title: bool = False):
    text = html_to_text(text)
    text = text.replace("\r", "").replace("\t", " ")
    text = re.sub('[ ]+', ' ', text)
    text = re.sub('[\n]+', '\n', text)

    text = zhconv.convert(text, "zh-hans")
    text = strQ2B(text)
    text = space_patten.sub(r'\1\2', text)
    text = space_patten.sub(r'\1\2', text)

    text = "\n".join([line for line in text.split('\n') if is_qualified_line(line)])
    if is_title:
        text = re.sub('[^a-zA-Z0-9\u4e00-\u9fa5]', '', text)

    lines = text.split('\n')
    lines = [line.strip() for line in lines]
    lines = [line for line in lines if len(line) > 0]
    text = "\n".join(lines)

    return text.strip()


def is_qualified_line(line: str):
    keywords = ["公司地址", "邮编", "附录", "网址", "热线电话", "请勿用于", "正版", "邮箱"]
    w_line = re.sub(r'[a-zA-Z0-9:@;\\-\\.]', '', line)
    w_line = w_line.replace("【", "").replace("】", "")

    if len(line) < 2 or len(w_line) * 2 < len(line):
        return False

    head = w_line[:8]
    tail = w_line[-8:]
    for keyword in keywords:
        if keyword in head or keyword in tail:
            return False

    return True


def output_article(source, title, content) -> Tuple[str, str]:
    title = re.sub(r'^[0-9]+[\\.\-]', '', title)
    title = format_text(title, True)

    content = format_text(content)
    if len(title) < 2 or len(content) < 50:
        return title, "not qualified"

    text_file = os.path.join(base_path, f"tcm_pt/{title}-{source}.txt")
    meta_file = os.path.join(base_path, f"tcm_pt/meta/{title}-{source}.meta")

    if os.path.exists(text_file) and os.path.exists(meta_file):
        try:
            with open(meta_file, 'r', encoding='utf8') as fp:
                meta = json.load(fp)

            if meta['size'] == len(content) and meta['title'] == f"{title}-{source}":
                return title, "skipping"
        except:
            pass

    with open(text_file, 'w', encoding='utf8') as fp:
        fp.write(content)

    if os.path.exists(meta_file):
        try:
            with open(meta_file, 'r', encoding='utf8') as fp:
                meta = json.load(fp)
        except:
            meta = {}
    else:
        meta = {}

    meta['size'] = len(content)
    meta['title'] = f"{title}-{source}"

    with open(meta_file, 'w', encoding='utf8') as fp:
        fp.write(json.dumps(meta))

    return title, "saved"


if __name__ == '__main__':
    format_text("古今图书集成-清-陈梦雷-博物汇编艺术典医部全录卷211至卷211-皮门", True)