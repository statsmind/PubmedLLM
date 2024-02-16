import scrapy
from past.builtins import unichr
from scrapy.http import HtmlResponse, Response
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.url import parse_url
import urllib.parse as urlparse


class Spider(scrapy.Spider):
    name = "zlnow"
    allowed_domains = ["www.zlnow.com"]
    start_urls = ["http://www.zlnow.com/"]

    def parse(self, response: Response, **kwargs):
        extractor = LinkExtractor(allow_domains=self.allowed_domains)
        urls = extractor.extract_links(response)
        urls = [url for url in urls if self.is_url_allowed(url)]
        yield from response.follow_all(urls=urls)
        #
        # for url in urls:
        #     if "yuedu_one.php" in url.url:
        #         result = parse_url(url.url)
        #         params = urlparse.parse_qs(result.query)
        #         name = params.get("name")[0]
        #         id = params.get("id")[0]
        #
        #         print("yuedu -> book", f"http://{result.hostname}/book/book_show.php?id={id}&name={name}")
        #         yield response.follow(url=f"http://{result.hostname}/book/book_show.php?id={id}&name={name}")

    def is_url_allowed(self, url):
        if "/html/" in url.url:
            return False

        if url.url.endswith("/") or url.url.endswith(".html") or url.url.endswith(".htm"):
            return True
        else:
            return False
