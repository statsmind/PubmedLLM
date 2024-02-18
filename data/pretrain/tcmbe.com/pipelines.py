# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html
import json

# useful for handling different item types with a single interface
from itemadapter import ItemAdapter


class Pipeline:
    # def __init__(self):
    #     self.output_file = r"z:\datasets\medtiku.com\medtiku.jsonl"
    #     with open(self.output_file, "w", encoding="utf-8") as fp:
    #         fp.write("")

    def process_item(self, item, spider):
        # with open(self.output_file, "a", encoding="utf-8") as fp:
        #     fp.write(json.dumps(item, ensure_ascii=False) + "\n")

        return None
