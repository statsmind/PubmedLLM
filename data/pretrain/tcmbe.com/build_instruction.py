import json
import random
import re
import string
from typing import List

from lxml import etree


def questions_to_map(questions: List[str]):
    if questions[0][0] == 'A' and questions[1][0] == 'B':
        return {q[0]: q for q in questions}
    else:
        return {chr(ord('A') + idx): chr(ord('A') + idx) + " " + q for idx, q in enumerate(questions)}


# def remove_html_tags(text):
#     parser = etree.HTMLParser()
#     tree = etree.fromstring(text, parser)
#     try:
#         return etree.tostring(tree, encoding='utf-8', method='text')
#     except:
#         return text


def process_qtype_1(quiz):
    r = random.randint(0, 1)

    if quiz['answer'] is None or len(quiz['answer']) == 0:
        yield
        return

    quiz['answer'] = quiz['answer'].strip()
    quiz['answer'] = re.sub('[^a-zA-Z]', '', quiz['answer'])

    questions = [quiz[alphabet] for alphabet in list('abcdefghijklmnopqrstuvwzyx') if alphabet in quiz and len(quiz[alphabet]) > 0]
    # try:
    question_map = questions_to_map(questions)

    # except:
    #     pass
    question_text = "\n".join(questions)
    answer_text = question_map[quiz['answer']]

    note = quiz['note']
    if len(note) > 0:
        note = "\n" + note


    yield {
        'instruction': html_to_text(quiz['pre'] + quiz['title']),
        'input': html_to_text(question_text),
        'output': html_to_text(answer_text + note)
    }


def process_qtype_2(quiz):
    """
    多选题
    :param quiz:
    :return:
    """
    r = random.randint(0, 1)

    if quiz['answer'] is None or len(quiz['answer']) == 0:
        yield
        return

    print(quiz)
    quiz['answer'] = quiz['answer'].strip()
    quiz['answer'] = re.sub('[^a-zA-Z]', '', quiz['answer'])

    questions = [quiz[alphabet] for alphabet in list('abcdefghijklmnopqrstuvwzyx') if
                 alphabet in quiz and len(quiz[alphabet]) > 0]
    # try:
    question_map = questions_to_map(questions)
    question_text = "\n".join(questions)
    answer_text = "，".join([question_map[a] for a in list(quiz['answer'])])

    note = quiz['note']
    if len(note) > 0:
        note = "\n" + note

    yield {
        'instruction': html_to_text(quiz['pre'] + quiz['title']),
        'input': html_to_text(question_text),
        'output': html_to_text(answer_text + note)
    }


def process_qtype_3(quiz):
    """
    名词解释
    :param quiz:
    :return:
    """
    r = random.randint(0, 1)

    if quiz['note'] is None or len(quiz['note']) == 0:
        raise ValueError("no note")

    yield {
        'instruction': html_to_text(quiz['pre'] + "请解释中医名词\"" + quiz['title'] + "\""),
        'input': '',
        'output': html_to_text(quiz['note'])
    }


def process_qtype_4(quiz):
    """
    问答
    :param quiz:
    :return:
    """
    r = random.randint(0, 1)

    if quiz['note'] is None or len(quiz['note']) == 0:
        raise ValueError("no note")

    yield {
        'instruction': html_to_text(quiz['pre'] + quiz['title']),
        'input': '',
        'output': html_to_text(quiz['note'])
    }


def html_to_text(text):
    root = etree.HTML(text)
    if root is None:
        return text
    else:
        converted = etree.tostring(root, method='text', encoding='utf-8')
        if converted is None:
            return text

        converted = converted.decode('utf-8')
        converted = converted.replace('\t', ' ').replace('\r', '')
        converted = re.sub('[ ]+', ' ', converted)
        return converted.strip()


def generate_instructions():
    dataset = r'z:\datasets\medtiku.com\medtiku.jsonl'
    with open(dataset, 'r', encoding='utf8') as fp:
        data = [json.loads(l) for l in fp]

    for quiz in data:
        if quiz['pre'] is None:
            quiz['pre'] = ''

        if quiz['note'] is None:
            quiz['note'] = ''
        else:
            quiz['note'] = html_to_text(quiz['note'])

        try:
            if quiz['qtype'] == 1:
                yield from process_qtype_1(quiz)
            elif quiz['qtype'] == 2:
                yield from process_qtype_2(quiz)
            elif quiz['qtype'] == 3:
                yield from process_qtype_3(quiz)
            elif quiz['qtype'] == 4:
                yield from process_qtype_4(quiz)
            else:
                print("Unknown  type")
        except:
            pass


if __name__ == "__main__":
    out = open(r'Z:\datasets\medtiku.jsonl', 'w', encoding='utf8')
    for inst in generate_instructions():
        out.write(json.dumps(inst, ensure_ascii=False) + "\n")