# Define here the models for your scraped items
#
# See documentation in:
# https://docs.scrapy.org/en/latest/topics/items.html

import scrapy
from scrapy.item import Item,Field


class CommentcrawlerItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    URL = scrapy.Field()
    UserName = scrapy.Field() #아이디
    UserID = scrapy.Field() #아이디넘버
    WriteAt = scrapy.Field() #댓글 날짜
    Content = scrapy.Field() #댓글 내용
    
    pass
