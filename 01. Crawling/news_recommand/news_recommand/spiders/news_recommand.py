from urllib.request import urlopen
import scrapy
from news_recommand.items import NewsRecommandItem
import pandas as pd
import datetime
import numpy as np
import re
import time
import logging

class News_recommandCrawlerSpider(scrapy.Spider):
    
    name = "news_recommand"
    start_urls = ['http://search.naver.com/']
    crawled_url = []


    def start_requests(self):
        headers= {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
        start_date = '20221125'
        end_date = '20221130'
        sid2_list = [258,259,260,261,262,263,310,771]
        # 259: 금융, 258: 증권, 261: 산업/재계, 771: 중기/벤쳐, 260: 부동산, 262: 글로벌 경제, 310: 생활경제, 263: 경제일반
        url_list = []
        
        while True:
            if int(start_date) <= int(end_date):
                for i in sid2_list:
                    try: 
                        for j in range(1,10):
                            url = 'https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2={0}&sid1=101&date={2}&page={1}'.format(i,j,start_date)
                        # url = 'https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2={0}&sid1=101&date={1}'.format(i,start_date)
                            url_list.append(url)
                    except:
                        pass

                        
            else:
                break

            start_date =  pd.to_datetime(start_date) + datetime.timedelta(days=1)
            start_date = start_date.strftime('%Y%m%d')

        for url in url_list:
            yield scrapy.Request(url=url, callback=self.parse, headers=headers)


    def parse(self, response):
        item = NewsRecommandItem()
        item['category'] = response.xpath('//*[@id="main_content"]/div[1]/h3/text()').get()
        # item['date']= response.meta('date')
        for i in range(1,3):
            for j in range(1, 11):
                item['title'] = response.xpath('//*[@id="main_content"]/div[2]/ul[{0}]/li[{1}]/dl/dt[2]/a/text()'.format(i,j)).extract()
                item['content'] = response.xpath('//*[@id="main_content"]/div[2]/ul[{0}]/li[{1}]/dl/dd/span[1]/text()'.format(i,j)).extract()
                item['url'] = response.xpath('//*[@id="main_content"]/div[2]/ul[{0}]/li[{1}]/dl/dt[2]/a/@href'.format(i,j)).extract()

                yield item