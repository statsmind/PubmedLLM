import json
import os
import random
import re

with open('辨证案例.txt', 'r', encoding='utf8') as fp:
    lines = fp.readlines()

cases = []
buffer = []
for line in lines:
    if re.search(r'^\d+\.', line):
        if len(buffer) > 0:
            cases.append(buffer)
            buffer = []

    buffer.append(line.strip())

if len(buffer) > 0:
    cases.append(buffer)

fout = open('辨证案例.jsonl', 'w', encoding='utf8')

for case in cases:
    buffer = []

    title = case[0]
    input = ""
    zhengduan = ""
    fangyao = ""
    bianzheng = ""

    for line in case[1:]:
        if "诊断" in line[:4]:
            input = "".join(buffer)
            zhengduan = line
            buffer = []
            continue

        if "方药" in line[:6]:
            buffer.append(line)
            fangyao = "".join(buffer)
            buffer = []
            continue

        buffer.append(line)

    bianzheng = "".join(buffer)

    r = random.randint(0, 1)
    if r == 0:
        fout.write(json.dumps({
            'instruction': '根据以下患者信息，请给出诊断结果，适用的方剂以及辨证分析',
            'input': input,
            'output': zhengduan + "\n" + fangyao + "\n辨证 " + bianzheng
        }, ensure_ascii=False) + "\n")
    else:
        fout.write(json.dumps({
            'instruction': (input + "。该患者的诊断、方剂、辨证是什么？").replace("。。", "。"),
            'input': '',
            'output': zhengduan + "\n" + fangyao + "\n辨证 " + bianzheng
        }, ensure_ascii=False) + "\n")

    # fout.write(input + "\n")
    # fout.write(zhengduan + "\n")
    # fout.write(fangyao + "\n")
    # fout.write(bianzheng + "\n")
    # fout.write("-------------------------------\n")
    #fout.write(json.dumps({"input": input, "output": f"诊断: {zhengduan}\n方药: {fangyao}\n辨证: {bianzheng}"}, ensure_ascii=False, indent=4) + "\n")

# print(cases)