import inspect
import json
import os.path
import re
from functools import wraps
import hashlib
import requests
from Bio import Entrez
from math import ceil

from dotenv import load_dotenv
from lxml import etree
from zhipuai import ZhipuAI

load_dotenv()

ai_client = ZhipuAI()
Entrez.email = "jameshu@live.ccom"

pubmed_ids = []
retstart = 0
retmax = 1000


class Cache:
    def __init__(self, root_path):
        self.root_path = root_path

    def bucket(self, name):
        def decorator(func):
            @wraps(func)
            def decorated(*args, **kwargs):
                sig = inspect.signature(func)
                params = sig.parameters

                param_names = [key for key in params.keys()]
                param_dict = {}
                param_dict.update(zip(params.keys(), args))
                param_dict.update(kwargs)

                for k in (params.keys() - param_dict.keys()):
                    param_dict[k] = params[k].default

                key = list(sorted(param_dict.items()))
                key = json.dumps(key)
                m = hashlib.md5()
                m.update(key.encode('utf8'))
                hashkey = m.hexdigest()

                cache_file = os.path.join(self.root_path, name, hashkey[0:2], hashkey)
                os.makedirs(os.path.dirname(cache_file), 0o777, exist_ok=True)

                if os.path.exists(cache_file):
                    with open(cache_file, 'r', encoding='utf8') as fp:
                        try:
                            result = json.load(fp)
                        except:
                            result = None

                        if result is not None:
                            return result

                result = func(*args, **kwargs)
                if result is not None:
                    with open(cache_file, 'w', encoding='utf8') as fp:
                        fp.write(json.dumps(result))

                return result

            return decorated
        return decorator


cache = Cache(".cache")


@cache.bucket("justscience")
def query_justscience(issn):
    if issn is None or len(issn) == 0:
        return None

    response = requests.get(
        f"https://sci.justscience.cn/list?sci=1&q={issn}&research_area=&If_range_min=&If_range_max=&jcr_quartile=0&oa=2&Self_cites_ratio_min=&Self_cites_ratio_max=&mainclass=0&subclass=0&pub_country=&not_pub_country=&sci_type=2&pub_frequency=7&adv=1")
    root = etree.HTML(response.text)
    tr_node = root.find(".//table[@class=\"s-result-table\"]//tbody//tr")
    if tr_node is None:
        response = requests.get(
            f"https://sci.justscience.cn/list?sci=0&q={issn}&research_area=&If_range_min=&If_range_max=&jcr_quartile=0&oa=2&Self_cites_ratio_min=&Self_cites_ratio_max=&mainclass=0&subclass=0&pub_country=&not_pub_country=&sci_type=2&pub_frequency=7&adv=1")
        root = etree.HTML(response.text)
        tr_node = root.find(".//table[@class=\"s-result-table\"]//tbody//tr")

    if tr_node is None:
        lines = []
    else:
        tr_text = etree.tostring(tr_node, method='text', encoding='utf8')
        lines = tr_text.decode().split("\n")
        lines = [line.strip() for line in lines]

    return lines


@cache.bucket("efetch")
def fetch_pubmed(pmid):
    handle = Entrez.efetch(db="pubmed", id=pmid)
    return handle.read().decode('utf8')


@cache.bucket("esearch")
def search_pubmed(term, retmax: int = 2000):
    handle = Entrez.esearch(db="pubmed", retmax=retmax, retstart=0, term=term, sort="Pub Date")
    return Entrez.read(handle)


@cache.bucket("embedding")
def get_embedding(text):
    response = ai_client.embeddings.create(input=text, model='embedding-2')
    return response.data[0].embedding
    # client = ZhipuAI(api_key="")  # 填写您自己的APIKey
    # response = client.chat.completions.create(
    #     model="glm-3-turbo",  # 填写需要调用的模型名称
    #     messages=[
    #         {"role": "user", "content": "作为一名营销专家，请为我的产品创作一个吸引人的slogan"},
    #         {"role": "assistant", "content": "当然，为了创作一个吸引人的slogan，请告诉我一些关于您产品的信息"},
    #         {"role": "user", "content": "智谱AI开放平台"},
    #         {"role": "assistant", "content": "智启未来，谱绘无限一智谱AI，让创新触手可及!"},
    #         {"role": "user", "content": "创造一个更精准、吸引人的slogan"}
    #     ],
    # )
    # print(response.choices[0].message)


def string_to_float(text) -> float:
    try:
        return float(text)
    except:
        return 0.


def parse_pubmed(content: str):
    root = etree.XML(content)

    title_node = root.find(".//ArticleTitle")
    if title_node is not None and title_node.text is not None:
        title = title_node.text.strip()
    else:
        title = ""

    abstract_node = root.find(".//AbstractText")
    if abstract_node is not None and abstract_node.text is not None:
        abstract = abstract_node.text.strip()
    else:
        abstract = ""

    issn_node = root.find(".//ISSN")
    if issn_node is not None and issn_node.text is not None:
        issn = issn_node.text.strip()
    else:
        issn = ""

    return dict(title=title, abstract=abstract, issn=issn)


candidates = []

search_result = search_pubmed("stroke")
for idx, pmid in enumerate(search_result['IdList']):
    content = fetch_pubmed(pmid)
    info = parse_pubmed(content)

    if_info = query_justscience(info['issn'])
    if if_info is None or len(if_info) == 0 or string_to_float(if_info[7]) < 4.0:
        continue

    info['embedding'] = get_embedding(info['title'] + "\n" + info['abstract'])
    candidates.append(info)


from sklearn.cluster import KMeans

X = [info['embedding'] for info in candidates]

# 把所有文章分成10个类
cluster = KMeans(n_clusters=10, random_state=0).fit(X)
for idx, label in enumerate(cluster.labels_):
    candidates[idx]['label'] = label


print(cluster)