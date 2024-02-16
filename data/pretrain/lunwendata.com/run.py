from scrapy.crawler import CrawlerProcess
from scrapy.exceptions import DropItem
from scrapy.settings import Settings
from scrapy.utils.project import get_project_settings
# from spiders import Spider
import base64
import json
import re
from typing import Iterable

import scrapy
from past.builtins import unichr
from scrapy import Request, signals
from scrapy.http import HtmlResponse, Response
from scrapy.link import Link
from scrapy.linkextractors import LinkExtractor
from scrapy.utils.url import parse_url
import urllib.parse as urlparse
from lxml import etree

from data.pretrain.utils import output_article


class Spider(scrapy.Spider):
    name = "lunwendata"
    allowed_domains = ["www.lunwendata.com"]
    start_urls = [
        "https://www.lunwendata.com/1503.html",
        "https://www.lunwendata.com/1325.html",
        "https://www.lunwendata.com/1159.html"
    ]

    def parse(self, response: Response, **kwargs):
        if "thesis" in response.url:
            root = etree.HTML(response.text)
            root = root.find(".//div[@id=\"article\"]")

            title_node = root.find(".//h1")
            if title_node is None:
                return

            content_node = root.find(".//div[@id=\"content\"]")
            if content_node is None:
                return

            title = etree.tostring(title_node, method="text", encoding='utf8').decode('utf8')
            content = etree.tostring(content_node, method="text", encoding='utf8').decode('utf8')
            yield dict(title=title, content=content)

            return

        extractor = LinkExtractor(allow_domains=self.allowed_domains)
        links = extractor.extract_links(response)
        links = [link for link in links if self.is_url_allowed(link)]
        for link in links:
            link.url = link.url.replace("http://", "https://")

        yield from response.follow_all(urls=links, meta={
            'download_timeout': 20
        })

    def is_url_allowed(self, url):
        result = parse_url(url.url)
        if re.match(r'^/thesis/\d+/', result.path):
            return True

        if re.match(r'^/1503_\d+.html', result.path) or re.match(r'^/1325_\d+.html', result.path) or re.match(
                r'^/1159_\d+.html', result.path):
            return True

        return False


class Pipeline:
    def open_spider(self, spider):
        pass

    def close_spider(self, spider):
        pass

    def process_item(self, item, spider):
        title, result = output_article("lunwendata", item['title'], item['content'])
        print(title, result)
        return None


class SpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s
    #
    # def process_spider_input(self, response, spider):
    #     # Called for each response that goes through the spider
    #     # middleware and into the spider.
    #
    #     # Should return None or raise an exception.
    #     return None
    #
    # def process_spider_output(self, response, result, spider):
    #     # Called with the results returned from the Spider, after
    #     # it has processed the response.
    #
    #     # Must return an iterable of Request, or item objects.
    #     for i in result:
    #         yield i
    #
    # def process_start_requests(self, start_requests, spider):
    #     # Called with the start requests of the spider, and works
    #     # similarly to the process_spider_output() method, except
    #     # that it does not have a response associated.
    #
    #     # Must return only requests (not items).
    #     for r in start_requests:
    #         yield r
    #
    # def process_spider_exception(self, response, exception, spider):
    #     # Called when a spider or process_spider_input() method
    #     # (from other spider middleware) raises an exception.
    #
    #     # Should return either None or an iterable of Request or item objects.
    #     pass

    def spider_opened(self, spider) -> None:
        spider.logger.info("Spider opened: %s" % spider.name)


class DownloaderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the downloader middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_request(self, request: Request, spider):
        # Called for each request that goes through the downloader middleware.
        request.meta["download_timeout"] = 20
        # Must either:
        # - return None: continue processing this request
        # - or return a Response object
        # - or return a Request object
        # - or raise IgnoreRequest: process_exception() methods of
        #   installed downloader middleware will be called
        return None

    # def process_response(self, request, response: Response, spider):
    #     # Called with the response returned from the downloader.
    #     # Must either;
    #     # - return a Response object
    #     # - return a Request object
    #     # - or raise IgnoreRequest
    #     return response
    #
    # def process_exception(self, request, exception, spider):
    #     # Called when a download handler or a process_request()
    #     # (from other downloader middleware) raises an exception.
    #
    #     # Must either:
    #     # - return None: continue processing this exception
    #     # - return a Response object: stops process_exception() chain
    #     # - return a Request object: stops process_exception() chain
    #     pass
    #
    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)


if __name__ == '__main__':
    settings = Settings()
    settings['BOT_NAME'] = 'spider'
    settings['ROBOTSTXT_OBEY'] = False
    settings['CONCURRENT_REQUESTS'] = 2
    settings['DOWNLOAD_DELAY'] = 0
    settings['CONCURRENT_REQUESTS_PER_DOMAIN'] = 2
    settings['CONCURRENT_REQUESTS_PER_IP'] = 2
    settings['DEFAULT_REQUEST_HEADERS'] = {
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "zh-CN",
    }
    settings['HTTPCACHE_ENABLED'] = True
    settings['HTTPCACHE_EXPIRATION_SECS'] = 3600000
    settings['HTTPCACHE_DIR'] = r"Z:\datasets\lunwendata.com\httpcache"
    settings['HTTPCACHE_IGNORE_HTTP_CODES'] = [400, 404, 500, 505]
    settings['HTTPCACHE_STORAGE'] = "scrapy.extensions.httpcache.FilesystemCacheStorage"
    settings['REQUEST_FINGERPRINTER_IMPLEMENTATION'] = "2.7"
    settings['TWISTED_REACTOR'] = "twisted.internet.asyncioreactor.AsyncioSelectorReactor"
    settings['FEED_EXPORT_ENCODING'] = "utf-8"
    settings['SPIDER_MIDDLEWARES'] = {
        SpiderMiddleware: 100,
    }
    settings['DOWNLOADER_MIDDLEWARES'] = {
        DownloaderMiddleware: 100
    }
    settings['ITEM_PIPELINES'] = {
        Pipeline: 300,
    }

    crawler_process = CrawlerProcess(settings=settings)
    crawler_process.crawl(Spider)
    crawler_process.start()
