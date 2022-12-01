from urllib.request import urlopen
import scrapy
from news_recommand.items import NewsRecommandItem
import pandas as pd
import datetime
import numpy as np
import requests
from bs4 import BeautifulSoup
import re
import time

class News_recommandCrawlerSpider(scrapy.Spider):
    
    name = "news_recommand"
    start_urls = ['http://search.naver.com/']
    crawled_url = []

    def start_requests(self):
        urls = []
        headers= {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}

        sid2_list = [258]#,259,260,261,262,263,310,771]

        for sid2 in sid2_list:
            for term in range(0, 3):
                date = (datetime.date(2022, 11,29) + datetime.timedelta(+term)).strftime('%Y%m%d')
                try: 
                    url = f'https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2={sid2}&sid1=101&date={date}'
                    urls.append(url)
                except Exception as e:
                    print(e)
                    pass

        for url in urls:
            yield scrapy.Request(url=url, callback=self.page_parse, headers=headers)

    def page_parse(self,response):
        headers= {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
        temp = response.url +'&page=200'
        print(temp)
        response_temp = requests.get(temp,headers=headers)
        soup = BeautifulSoup(response_temp.text, 'html.parser')
        end_pages = soup.select('.paging strong')[0].text
        for end_page in range(1,int(end_pages)+1):
                yield scrapy.Request(url=response.url+'&page='+str(end_page), callback=self.crawl_parse, headers=headers)

    
    
    def crawl_parse(self,response):
        page_urls = []
        headers= {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
        
        for i in range(1,3):
            for j in range(1,11):
                try:
                    page_urls.append(response.xpath(f'//*[@id="main_content"]/div[2]/ul[{i}]/li[{j}]/dl/dt[1]/a/@href')[0].extract())
                    print(response.xpath(f'//*[@id="main_content"]/div[2]/ul[{i}]/li[{j}]/dl/dt[1]/a/@href')[0].extract())
                except Exception as e:
                    print(e)
                    pass
        
        # for url in page_urls:
        #     yield scrapy.Request(url=url, callback=self.parse, headers=headers)
