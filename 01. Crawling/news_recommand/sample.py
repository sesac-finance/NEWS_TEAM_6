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
    
    name = "new_recommand"
    start_urls = ['http://search.naver.com/']
    crawled_url = []


    def start_requests(self):
        headers= {
        'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/107.0.0.0 Safari/537.36'}
        start_date = '20221130'
        end_date = '20221130'
        sid2_list = [258,259,260,261,262,263,310,771]
        # 259: 금융, 258: 증권, 261: 산업/재계, 771: 중기/벤쳐, 260: 부동산, 262: 글로벌 경제, 310: 생활경제, 263: 경제일반
        url_list = []
        
        while True:
            if int(start_date) <= int(end_date):
                for i in sid2_list:
                    # for j in range(1,100):
                        # url = 'https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2={0}&sid1=101&date={2}&page={1}'.format(i,j,start_date)
                    url = 'https://news.naver.com/main/list.naver?mode=LS2D&mid=shm&sid2={0}&sid1=101&date={1}'.format(i,start_date)
                    url_list.append([url, start_date])
            else:
                break

            start_date =  pd.to_datetime(start_date) + datetime.timedelta(days=1)
            start_date = start_date.strftime('%Y%m%d')

        for url, date in url_list:
            yield scrapy.Request(url=url, meta = {'date': date}, callback=self.parse_news, headers=headers)

    def parse_news(self, response):
        if response.url not in self.crawled_url:
            self.crawled_url.append(response.url)
            //*[@id="main_content"]/div[2]/ul[1]/li[1]/dl/dt[2]/a
            //*[@id="main_content"]/div[2]/ul[2]/li[1]/dl/dt[2]/a
            articles = response.xpath('//*[@id="main_content"]/div[2]/ul/li')
            category = response.xpath('//*[@id="main_content"]/div[1]/h3/text()').get()
            for article in articles:
                title = article.xpath('./dl/dt/a/text()').get()
                title_url = article.xpath('./dl/dt/a/@href').get()
                content = article.xpath('./dl/dd/span[1]/text()').get()
                cur_date = response.meta['date']
                title_url_fake_user = title_url
                yield scrapy.Request(
                    title_url_fake_user,
                    callback=self.parse_page,
                    meta={"title": title, "date": cur_date, 'url': title_url, 'content':content, 'category':category},
                )
        # next_page = response.xpath('//*[@id="main_content"]/div[3]/a/@href')
        # print('--------------------------------------')
        # print(next_page)
        # if next_page != []:
        #     yield response.follow(
        #         next_page[-1].get(),
        #         meta={'date': cur_date},
        #         callback=self.parse_news)

    def parse_page(self, response):
        # logging.info("response.status:%s" %response.status)
        # loggurl = response.selector.css('div.main-nav__logo img').xpath('@src').extract()
        # logging.info('response.loggurl:%s' % loggurl)

        item = NewsRecommandItem()
        item["title"] = response.meta["title"]
        item["date"] = response.meta["date"]
        item["url"] = response.meta["url"]
        item['content'] = response.meta['content']
        item['category'] = response.meta['category']
        # item['content'] = response.xpath('//*[@id="main_content"]/div[2]/ul/li/dl/dd/span[1]/text()').extract()
        yield item

        # category = response.xpath('//*[@id="main_content"]/div[1]/h3/text()').extract()
        # title = response.xpath('//*[@id="main_content"]/div[2]/ul/li/dl/dt[2]/a/text()').extract()
        # title_url = response.xpath('//*[@id="main_content"]/div[2]/ul[{i}]/li[{j}]/dl/dt[2]/a/@href').extract()


        # if item["t"] == "연합인포맥스":
        #     time.sleep(0.2)
        #     title = response.xpath('//*[@id="user-container"]/div[3]/header/div/div/text()').get()
        #     content = response.xpath('//*[@id="article-view-content-div"]/text()').getall()
        # elif item["media"] == "이데일리":
        #     title = response.xpath('//*[@id="contents"]/section[1]/section[1]/div[1]/div[1]/h2/text()').get()
        #     content = response.xpath(
        #         '//*[@id="contents"]/section[1]/section[1]/div[1]/div[3]/div[1]/text()').getall()
        # else:
        #     # 연합뉴스
        #     if 'naver' in response.url:
        #         title = response.xpath('//*[@id="ct"]/div[1]/div[2]/h2/text()').get()
        #         content = response.xpath('//*[@id="dic_area"]/text()').getall()
        #     else:
        #         title = response.xpath('//*[@id="articleWrap"]/div[1]/header/h1/text()').get()
        #         content = response.xpath('//*[@id="articleWrap"]/div[2]/div/div/article/p/text()').getall()

                # else:
                #     item['category'] =  .format(i, j)).extract()
                #     item['title'] =  response.xpath('//*[@id="main_content"]/div[2]/ul[{i}]/li[{j}]/dl/dt[2]/a/text()'.format(i, j)).extract()
                #     item['title_url'] = response.xpath('//*[@id="main_content"]/div[2]/ul[{i}]/li[{j}]/dl/dt[2]/a/@href'.format(i, j)).extract()
                    # item['press'] = response.xpath('//*[@id="sp_nws{0}"]/div/div/div[1]/div[2]/a/@href'.format(i)).extract()
                #     item['date'] = response.xpath('//*[@id="sp_nws{0}"]/div/div/div[1]/div[2]/span/text()'.format(i, j)).extract()

                # add_url = item['pdf_url'][0]
                # with open('./pdf/{}.pdf'.format(item['title']), mode='wb') as f:
                #     f.write(urlopen(add_url).read())

                # yield item

    # def file_download_from_web(url: str, file_name: str, file_extension: str):
    #     download = urlopen(url).read()
    #     file = './files/' + file_name + '.' + file_extension
