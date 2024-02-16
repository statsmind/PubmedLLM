import json
import os

from data.pretrain.utils import output_article

if __name__ == "__main__":
    for dirpath, dirnames, filenames in os.walk(r"Z:\datasets\dianji"):
        for filename in filenames:
            if not (filename.endswith(".txt") and filename.startswith("ft_")):
                continue

            print(filename)

            with open(os.path.join(dirpath, filename), "r", encoding="utf-8") as fp:
                content = fp.read()

            article_name = filename[3:-4]
            output_article("dianji", article_name, content)
