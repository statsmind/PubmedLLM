import json
import os

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
    outfile = open(r"z:\datasets\dianji.jsonl", "a", encoding="utf8")

    for dirpath, dirnames, filenames in os.walk(r"Z:\datasets\dianji"):
        for filename in filenames:
            if not (filename.endswith(".txt") and filename.startswith("ft_")):
                continue

            print(filename)

            with open(os.path.join(dirpath, filename), "r", encoding="utf-8") as fp:
                content = fp.read()

            outfile.write(json.dumps({"text": content}, ensure_ascii=False) + "\n")