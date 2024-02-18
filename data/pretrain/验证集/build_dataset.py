import json
import multiprocessing
import os.path
import re
import sys

from lxml import etree
from lxml.etree import _Element

from six import unichr


if __name__ == "__main__":
    outfile = open(r"Z:\datasets\tcm_valid.jsonl", "w", encoding="utf-8")
    for dirpath, dirnames, filenames in os.walk(r"Z:\datasets\验证集"):
        for filename in filenames:
            if not filename.endswith(".txt"):
                continue

            print(dirpath, filename)

            with open(os.path.join(dirpath, filename), 'r', encoding='utf8') as fp:
                content = fp.read().replace("\r", "").replace("\n\n", "\n").replace("\n\n", "\n")

            outfile.write(json.dumps({
                'text': content
            }, ensure_ascii=False) + "\n")
            outfile.flush()
