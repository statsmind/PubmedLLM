import base64
import json
from typing import Iterable

import scrapy
from past.builtins import unichr
from scrapy import Request
from scrapy.http import HtmlResponse, Response
from scrapy.link import Link
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.url import parse_url
import urllib.parse as urlparse


class Spider(scrapy.Spider):
    name = "medtiku"
    allowed_domains = ["www.medtiku.com"]
    start_urls = ["https://www.medtiku.com/"]

    def start_requests(self) -> Iterable[Request]:
        yield Request("https://www.medtiku.com/", meta={
            'type': 'home'
        })

    def parse(self, response: Response, **kwargs):
        try:
            extractor = LinkExtractor(allow_domains=self.allowed_domains)
            links: [Link] = extractor.extract_links(response)
        except:
            pass

        request = response.request
        if request.meta['type'] == 'home':
            for link in links:
                p = parse_url(link.url)
                if p.path == "/cat":
                    yield Request(link.url, meta={
                        'type': 'cat'
                    })
        elif request.meta['type'] == 'cat':
            for link in links:
                p = parse_url(link.url)
                if p.path == "/subject":
                    yield Request(link.url, meta={
                        'type': 'subject',
                        'sname': link.text
                    })
        elif request.meta['type'] == 'subject':
            for link in links:
                p = parse_url(link.url)
                if p.path != "/app":
                    continue

                fragment = p.fragment.split("/")
                if len(fragment) != 5:
                    continue

                sid, cid = fragment[2:4]
                yield response.follow(f"https://www.medtiku.com/api/q?cid={cid}&sid={sid}", meta={
                    'type': 'json',
                    'sid': sid,
                    'sname': request.meta['sname'],
                    'cid': cid,
                    'cname': link.text
                })
        elif request.meta['type'] == 'json':
            data = json.loads(response.text)
            data = base64.decodebytes(data['data']['quiz'].encode('utf8'))
            data = json.loads(data)
            for quiz in data:
                quiz['sid'] = request.meta['sid']
                quiz['sname'] = request.meta['sname']
                quiz['cid'] = request.meta['cid']
                quiz['cname'] = request.meta['cname']
                yield quiz

    def is_url_allowed(self, url):
        if "/html/" in url.url:
            return False

        if url.url.endswith("/") or url.url.endswith(".html") or url.url.endswith(".htm"):
            return True
        else:
            return False
