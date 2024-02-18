# Define here the models for your spider middleware
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/spider-middleware.html
import os.path
import random
import urllib.parse as urlparse
from typing import List

import scrapy.spidermiddlewares.httperror
from scrapy import signals, Request

# useful for handling different item types with a single interface
from itemadapter import is_item, ItemAdapter
from scrapy.crawler import Crawler
from scrapy.http import HtmlResponse, TextResponse, Response
from scrapy.utils.url import parse_url


class SpiderMiddleware:
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler: Crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, or item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Request or item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it does not have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

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

    def process_response(self, request, response: Response, spider):
        # Called with the response returned from the downloader.
        # Must either;
        # - return a Response object
        # - return a Request object
        # - or raise IgnoreRequest
        return response

    def get_local_cache_file(self, request):
        result = parse_url(request.url)
        hostname = result.hostname
        path = result.path
        if path.endswith("/"):
            path = path + "index.html"
        if path.startswith("/"):
            path = path[1:]

        if "zlnow.com" in hostname and (path == 'book/yuedu_one.php' or path == 'book/book_show.php'):
            path = "book/" + self.get_query_param(result.query, "id") + "_" + self.get_query_param(result.query, "pian", "0") + ".html"

        local_file = os.path.join(self.CACHE_DIR, path)
        os.makedirs(os.path.dirname(local_file), 0o777, exist_ok=True)

        return local_file

    def get_query_param(self, query, param, default=None):
        result = urlparse.parse_qs(query)
        if param not in result:
            return default

        value = result[param]
        if isinstance(value, List):
            if len(value) > 0:
                return value[0]
            else:
                return default
        else:
            return value

    def process_exception(self, request, exception, spider):
        # Called when a download handler or a process_request()
        # (from other downloader middleware) raises an exception.

        # Must either:
        # - return None: continue processing this exception
        # - return a Response object: stops process_exception() chain
        # - return a Request object: stops process_exception() chain
        # if "proxy" in request.meta:
        #     proxy = request.meta["proxy"].split("://")
        #     proxy = proxy[1] + "," + proxy[0]
        #     print("removing proxy", proxy)
        #     PROXIES.remove(proxy)

        pass

    def spider_opened(self, spider):
        spider.logger.info("Spider opened: %s" % spider.name)
