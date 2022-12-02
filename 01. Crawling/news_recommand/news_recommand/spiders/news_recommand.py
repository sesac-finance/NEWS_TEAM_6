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


    def start_requests(self):
        urls = []
        headers= {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}

        sid2_list = [260,771]#,258,259,260,261,262,263,310,771]

        # sub_category를 item에 담기 위해 sub2를 meta에 담음
        for sid2 in sid2_list:
            for term in range(0, 1):
                date = (datetime.date(2022, 11,29) + datetime.timedelta(+term)).strftime('%Y%m%d')
                try: 
                    url = f'https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2={sid2}&sid1=101&date={date}'
                    urls.append([url,sid2]) # url, sid2 리스트로 묶어 담기
                except Exception as e:
                    print(e)
                    pass

        for url,sid2 in urls:
            # sid2 meta로 저장
            yield scrapy.Request(url=url, meta = {'sid2': sid2}, callback=self.page_parse, headers=headers)

    def page_parse(self,response):
        headers= {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
        temp = response.url +'&page=200'
        # print(temp)
        response_temp = requests.get(temp,headers=headers)
        soup = BeautifulSoup(response_temp.text, 'html.parser')
        end_pages = soup.select('.paging strong')[0].text
        for end_page in range(1,int(end_pages)+1):
            sub_category = response.meta['sid2']
            yield scrapy.Request(url=response.url+'&page='+str(end_page), meta = {'sid2': sub_category}, callback=self.crawl_parse, headers=headers)

    
    
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
            sub_cate = response.meta['sid2']
            yield scrapy.Request(url=url, meta = {'sub2': sub_cate}, callback=self.parse, headers=headers)


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


        # category_dict로 sub_category 추출
        category_dict = {259: '금융', 258: '증권', 261: '산업/재계', 771: '중기/벤쳐', 260: '부동산', 262: '글로벌경제', 310: '생활경제', 263: '경제일반'}
        
        # 기사의 photo 개수에 따라 if문
        photo_counts = len(response.xpath('//*[@class="nbd_im_w _LAZY_LOADING_WRAP "]/div/img').getall())
        if photo_counts != 0:
            # 기사 photo 주소 list로 담기
            photo_list=[]
            for i in range(1, photo_counts+1):
                photo = response.xpath('//*[@id="img{0}"]/@data-src'.format(i)).get()
                photo_list.append(photo)

            item['photo'] = photo_list
            item['press'] = response.xpath('//*[@id="ct"]/div[1]/div[1]/a/img[1]/@title').get()
            item['date'] = response.xpath('//*[@id="ct"]/div[1]/div[3]/div[1]/div[1]/span/@data-date-time').get()
            item['reporter'] = response.xpath('//*[@id="contents"]/div/p/span/text()').get()
            item['title'] =response.xpath('//*[@id="title_area"]/span/text()').get()     
            item['sticker'] = sticker_dict
            item['url'] = response.xpath('//html/head/meta[6]/@content').get()
            category_num  = response.meta['sub2']
            item['sub_category'] = category_dict[category_num]
            
            print(item['sub_category'])

            content = response.xpath('//*[@id="contents"]/text()')
            if content != []:
                content = response.xpath('//*[@id="dic_area"]/text()').extract()
                item['content'] = [''.join(content[i].strip()) for i in range(len(content))]
                
            else:
                content = response.xpath('//*[@id="contents"]/text()').extract()
                item['content'] = [''.join(content[i].strip()) for i in range(len(content))]

            yield item

        else:
            item['press'] = response.xpath('//*[@id="ct"]/div[1]/div[1]/a/img[1]/@title').get()
            item['date'] = response.xpath('//*[@id="ct"]/div[1]/div[3]/div[1]/div[1]/span/@data-date-time').get()
            item['reporter'] = response.xpath('//*[@id="contents"]/div/p/span/text()').get()
            item['title'] =response.xpath('//*[@id="title_area"]/span/text()').get()  
            item['sticker'] = sticker_dict
            item['url'] = response.xpath('//html/head/meta[6]/@content').get()
            category_num  = response.meta['sub2']
            item['sub_category'] = category_dict[category_num]

            content = response.xpath('//*[@id="contents"]/text()')
            if content != []:
                content = response.xpath('//*[@id="dic_area"]/text()').extract()
                # print(content)
                item['content'] = [''.join(content[i].strip()) for i in range(len(content))]
                
            else:
                content = response.xpath('//*[@id="contents"]/text()').extract()
                # print(content)
                item['content'] = [''.join(content[i].strip()) for i in range(len(content))]
            
            yield item

        
