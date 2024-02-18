import os
import re
import sys
import chardet
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


if __name__ == "__main__":
    for dirpath, dirnames, filenames in os.walk(r"Z:\datasets\dianji"):
        for filename in filenames:
            if not filename.endswith(".txt") or filename.startswith("ft_"):
                continue

            outfile = "ft_" + filename
            if os.path.exists(outfile) and os.path.getsize(outfile) > 100:
                print(f"skipping {filename}")
                continue

            with open(filename, 'rb') as f:
                encoding = chardet.detect(f.read())['encoding']
                if encoding == "GB2312" or encoding is None:
                    encoding = "GB18030"

            print(filename, encoding)

            with open(filename, 'r', encoding=encoding) as fp:
                content = fp.read()

            content = strQ2B(content)
            content = content.replace("　", " ").replace("", " ")
            content = re.sub("[ \t]+", " ", content)

            lines = content.split("\n")
            lines = [line for line in lines if "上一页" not in line and "下一页" not in line and "当前页" not in line]
            lines = [re.sub("^[ 　]+", "\n", line) for line in lines]
            lines = [re.sub("。[ ]*$", "。\n", line) for line in lines]
            content = "\n".join(lines)

            content = re.sub("\n{2,}", '######', content)
            content = content.replace("\n", "")
            content = content.replace("######", "\n")

            lines = content.split("\n")
            lines = [line.strip(" \n-") for line in lines if len(line.strip(" \n-")) > 0]
            content = "\n".join(lines)

            with open(outfile, 'w', encoding='utf8') as fp:
                fp.write(content)
