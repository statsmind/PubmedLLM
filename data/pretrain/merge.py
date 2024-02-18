import json
import os

if __name__ == "__main__":
    fout = open('/nfs/datasets/tcm_pt.jsonl', 'w', encoding='utf8')

    for dirpath, dirnames, filenames in os.walk("/nfs/datasets/tcm_pt"):
        for filename in filenames:
            if filename.endswith(".txt"):
                continue

            filepath = os.path.join(dirpath, filename)
            with open(filepath, 'r', encoding='utf8') as fp:
                fout.write(json.dumps({
                    'text': fp.read()
                }, ensure_ascii=False))
