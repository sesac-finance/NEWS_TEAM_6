from urllib.request import urlopen
import scrapy
from commentcrawler.items import CommentcrawlerItem
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
            for term in range(0, 30):
                date = (datetime.date(2022, 11,1) + datetime.timedelta(+term)).strftime('%Y%m%d')
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
            yield scrapy.Request(url=url, callback=self.parse_comment, headers=headers)

    def parse_comment(self,response):
        item = CommentcrawlerItem() #items.py연결

        #referer 주소
        referer = response.xpath('/html/head/meta[6]/@content').get()
        print(referer)
        #header 조건
        headers = {'user-agent':'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36','referer':referer}

        # referer에서 기사 ID만 추출
        referer_x = referer.split('/')[5]
        referer_y = referer.split('/')[6].split('?')[0]


        #comment_url에 기사 ID url 호출 -> json text 추출
        comment_url = f'https://cbox5.apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json?ticket=news&templateId=view_economy_m1&pool=cbox5&_cv=20221122141410&_callback=jQuery33101007245602740896_1669950551257&lang=ko&country=KR&objectId=news{referer_x}%2C{referer_y}&categoryId=&pageSize=5&indexSize=10&groupId=&listType=OBJECT&pageType=more&page=1&initialize=true&userType=&useAltSort=true&replyPageSize=500&sort=relative&includeAllStatus=true&_=1669950551261'
        response_url = requests.get(comment_url,headers=headers)
        soup = BeautifulSoup(response_url.text, 'html.parser')
        json_text = soup.text
        data = re.findall('\{.*?\)+;',json_text)[0][:-2] #정규표현식으로 jQuery삭제
        result_comment = json.loads(data)

        for i in range(0, len(result_comment['result']['commentList'])):

            name = result_comment['result']['commentList'][i]['maskedUserName']
            id = result_comment['result']['commentList'][i]['userIdNo']
            date = result_comment['result']['commentList'][i]['regTime']
            contents = result_comment['result']['commentList'][i]['contents']
            print(referer)    
            item['URL'] = referer
            item['UserName'] = name #아이디
            item['UserID'] = id #아이디넘버
            item['WriteAt'] = date #댓글 날짜
            item['Content'] = contents #댓글 내용

            yield item

