# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from __future__ import unicode_literals
from scrapy.exporters import JsonItemExporter, CsvItemExporter
from itemadapter import ItemAdapter

import sys
#reload(sys)
#sys.setdefaultencoding('utf-8')

class CommentCrawlerPipeline(object):
    def open_spider(self,spider):
        self.file = open("comment.csv",'wb')
        self.exporter = CsvItemExporter(self.file,encoding='utf-8-sig')
        self.exporter.start_exporting()

    def close_spider(self,spider):
        self.exporter.finish_exporting()
        self.file.close() #파일 close

    def process_item(self,item,spider):
        self.exporter.export_item(item)
        return item
