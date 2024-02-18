import inspect
import json
import os.path
import re
from functools import wraps
import hashlib
import requests
from Bio import Entrez
from math import ceil
from lxml import etree
# from cacheout import Cache
#
# cache = Cache()
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


count = 0
search_result = search_pubmed("stroke")
for idx, pmid in enumerate(search_result['IdList']):
    content = fetch_pubmed(pmid)
    info = parse_pubmed(content)

    if info['issn'] != '':
        if_info = query_justscience(info['issn'])
        if len(if_info) > 0 and len(info['title']) > 50 and string_to_float(if_info[7]) >= 4.0:
            print(info['title'])
            # print("Title:", info['title'])
            # print("Abstract:", info['abstract'])
            # print("Impact Factor:", if_info[7])
            count += 1
    else:
        print(idx, pmid, "no issn")

print(count)