import base64
import json
import re
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
    name = "tcmbe"
    allowed_domains = ["www.tcmbe.com"]
    start_urls = ["https://www.tcmbe.com/"]

    def parse(self, response: Response, **kwargs):
        extractor = LinkExtractor(allow_domains=self.allowed_domains)
        urls = extractor.extract_links(response)
        urls = [url for url in urls if self.is_url_allowed(url)]
        yield from response.follow_all(urls=urls)

    def is_url_allowed(self, url):
        result = parse_url(url.url)
        if re.match(r'^/forums/\d+/', result.path) or re.match(r'^/threads/\d+/$', result.path):
            return True
        else:
            return False
        # if url.url.endswith("/") or url.url.endswith(".html") or url.url.endswith(".htm"):
        #     return True
        # else:
        #     return False
