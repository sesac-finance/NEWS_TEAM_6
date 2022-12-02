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
import itertools
import json

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
            for term in range(0, 1):
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
        # print(temp)
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
                except Exception as e:
                    # print(e)
                    pass
        
        for url in page_urls:
            yield scrapy.Request(url=url, callback=self.parse, headers=headers)


    def parse(self, response):
        item = NewsRecommandItem()
        
        # referer 주소
        referer = response.xpath('/html/head/meta[6]/@content').get()

        # headers 조건
        headers= {'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36',
                    'referer':referer}
        
        # referer에서 기사 ID만 추출
        referer_x = referer.split('/')[5]
        referer_y = referer.split('/')[6].split('?')[0]

        # sticker_url에 기사 ID url 호출 -> json text 추출
        sticker_url = 'https://news.like.naver.com/v1/search/contents?suppress_response_codes=true&q=JOURNALIST%7CNEWS%5Bne_{0}%5D&isDuplication=false'.format(referer_x+'_'+referer_y)
        response_url= requests.get(sticker_url, headers=headers)

        soup = BeautifulSoup(response_url.text, 'html.parser')
        json_text = soup.text
        json_text

        test2 = json.loads(json_text)

        # json text에서 sticker와 count 추출해서 list 담기
        sticker_temp= []
        sticker_cnt_temp = []
        for i in range(0, len(test2['contents'][0]['reactions'])):
                sticker = test2['contents'][0]['reactions'][i]['reactionTypeCode']['description']
                sticker_count = test2['contents'][0]['reactions'][i]['count']
                sticker_temp.append(sticker)
                sticker_cnt_temp.append(sticker_count)
        
        sticker_dict = {x:y for x,y in zip(sticker_temp,sticker_cnt_temp)}




        # sticker_temp = []
        # sticker_cnt_temp = []
        # for i in range(1,6):
        #     sticker = response.xpath('//*[@id="likeItCountViewDiv"]/ul/li[{0}]/a/span[1]/text()'.format(i)).extract()
        #     sticker_count = response.xpath('//*[@id="likeItCountViewDiv"]/ul/li[{0}]/a/span[2]/text()'.format(i)).get()
        #     sticker_temp.append(sticker)
        #     sticker_cnt_temp.append(sticker_count)
        # sticker_temp = list(itertools.chain(*sticker_temp))
        # # print(sticker_cnt_temp)
        # # print(sticker_temp)
        
        # sticker_dict = {x:y for x,y in zip(sticker_temp, sticker_cnt_temp)}
        
        # print(sticker_dict)

        
        # sticker.dict = {'sticker':sticker_count}

        # print(sticker_dict)

        photo_counts = len(response.xpath('//*[@class="nbd_im_w _LAZY_LOADING_WRAP "]/div/img').getall())
        if photo_counts != 0:
            for i in range(1, photo_counts+1):
                item['photo'] = response.xpath('//*[@id="img{0}"]/@data-src'.format(i)).get()
                item['press'] = response.xpath('//*[@id="ct"]/div[1]/div[1]/a/img[1]/@title').get()
                item['date'] = response.xpath('//*[@id="ct"]/div[1]/div[3]/div[1]/div[1]/span/@data-date-time').get()
                item['reporter'] = response.xpath('//*[@id="contents"]/div/p/span/text()').get()
                item['title'] =response.xpath('//*[@id="title_area"]/span/text()').get()     
                item['sticker'] = sticker_dict
                item['url'] = response.xpath('//html/head/meta[6]/@content').get()

                content = response.xpath('//*[@id="contents"]/text()')
                if content != []:
                    content = response.xpath('//*[@id="dic_area"]/text()').getall()
                    item['content'] = content
                    
                else:
                    content = response.xpath('//*[@id="contents"]/text()').getall()
                    item['content'] = content

                yield item

        else:
            for i in range(1,6):
                # item['sticker'] = response.xpath('//*[@id="likeItCountViewDiv"]/ul/li[{0}]/a/span[1]/text()'.format(i)).extract()
                # item['sticker_count'] = response.xpath('//*[@id="likeItCountViewDiv"]/ul/li[{0}]/a/span[2]'.format(i)).getall()
                item['press'] = response.xpath('//*[@id="ct"]/div[1]/div[1]/a/img[1]/@title').get()
                item['date'] = response.xpath('//*[@id="ct"]/div[1]/div[3]/div[1]/div[1]/span/@data-date-time').get()
                item['reporter'] = response.xpath('//*[@id="contents"]/div/p/span/text()').get()
                item['title'] =response.xpath('//*[@id="title_area"]/span/text()').get()  
                item['sticker'] = sticker_dict
                item['url'] = response.xpath('//html/head/meta[6]/@content').get()

                content = response.xpath('//*[@id="contents"]/text()')
                if content != []:
                    content = response.xpath('//*[@id="dic_area"]/text()').getall()
                    item['content'] = content


                else:
                    content = response.xpath('//*[@id="contents"]/text()').getall()
                    item['content'] = content


                yield item
