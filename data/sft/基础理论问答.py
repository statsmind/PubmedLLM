import json
import re


def extract_qa(text):
    lines = text.split("\n")
    q = ""
    a = ""
    results = []
    for line in lines:
        if re.match("^[0-9]+、", line):
            if len(a.strip()) > 0:
                results.append([q, a.strip()])

            q = line
            a = ""
        else:
            a += "\n" + line

    results.append([q, a])
    return results


def format_answer(answer):
    answer = answer.strip()
    answer = answer.replace("\r", "").replace("\n\n", "\n").replace("\n\n", "\n").replace("答：", "")
    return answer.strip()


def format_question(question):
    question = question.strip()
    question = re.sub("^[0-9]+、", "", question)
    return question.strip()


if __name__ == "__main__":
    is_answer_section = False
    parts = []
    part = ""

    with open('基础理论问答.txt', 'r', encoding='utf-8') as fp:
        for line in fp:
            if re.match('^第.*章', line.strip()):
                if "答案" in line:
                    is_answer_section = True

            if not is_answer_section:
                continue

            if re.match('^第.*章', line.strip()):
                if len(part) > 0:
                    parts.append(part)
                part = line
            else:
                part = part + "\n" + line

        if len(part) > 0:
            parts.append(part)

    out = open('基础理论知识.jsonl', 'w', encoding='utf-8')

    for part in parts:
        pos1 = part.index("（一）简答题")
        pos2 = part.index("（二）论述题")

        jianda = part[pos1 + 8: pos2]
        lunshu = part[pos2 + 8:]

        jianda_qa = extract_qa(jianda)
        lunshu_qa = extract_qa(lunshu)

        for qa in jianda_qa:
            out.write(json.dumps({
                'instruction': format_question(qa[0]),
                'input': '',
                'output': format_answer(qa[1])
            }, ensure_ascii=False) + "\n")

        for qa in lunshu_qa:
            out.write(json.dumps({
                'instruction': format_question(qa[0]),
                'input': '',
                'output': format_answer(qa[1])
            }, ensure_ascii=False) + "\n")

        print(pos1, pos2)

    print(parts)
