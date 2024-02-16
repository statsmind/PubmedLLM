from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders import Spider

if __name__ == '__main__':
    crawler_process = CrawlerProcess(get_project_settings())
    crawler_process.crawl(Spider, 'all')
    crawler_process.start()
