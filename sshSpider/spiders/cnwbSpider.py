# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from urllib import parse
import re
import datetime

from sshSpider.items import NewsItem,MyItemLoader
from sshSpider.utils.common import get_md5


#爬取网站：中国防水协会网
#爬取信息：新闻动态
class CnwbSpider(scrapy.Spider):
    name = 'cnwbSpider'
    allowed_domains = ['http://www.cnwb.net']
    start_urls = ['http://www.cnwb.net/list/news/2.html']

    #获取中国防水网新闻动态的分类页的URL
    def parse(self, response):
        category_list = response.xpath("//div[@class = 'jquery-accordion-menu']/ul/li/a/@href").extract()
        for category_url in category_list:
            url=parse.urljoin(response.url, category_url)
            yield Request(url=parse.urljoin(response.url,category_url),callback=self.parse_list,dont_filter=True)


    #获取各分类的列表信息
    def parse_list(self, response):
        #1 爬取当前页列表各项动态的url，交给scrapy下载，之后使用parse_detail解析
        list_item_url = response.xpath("//ul[@class='newul']/li/a/@href").extract()
        for item_url in list_item_url:
            yield Request(url=parse.urljoin(response.url,item_url),callback=self.parse_detail,dont_filter=True)
        #2 爬取下一页的url，并交给scrapy下载，之后使用parse_list解析
        next_url = response.xpath("//ul[@class='pagination']/li[@class='next']/a/@href").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse_list,dont_filter=True)


    #获取分类中各条信息的详情
    def parse_detail(self,response):
        detail_item = NewsItem()
        # title = response.xpath("//font[@class = 'ttt']/text()").extract_first()
        # date_str = response.xpath("//span[@class='xhjstime']/text()").extract_first().strip()
        # match = re.search('(\d{4}/\d{1,2}/\d{1,2})', date_str)
        # if match:
        #     date = match.group()
        # try:
        #     date = datetime.datetime.strptime(date,"%Y/%m/%d").date()
        # except Exception as e:
        #     date = datetime.datetime.now().date()
        # content = response.xpath("//div[@class='clearFloat xhp']").extract_first()
        # url = response.url
        tag_list = [response.xpath('//span[@class="abwz"]/a[3]/text()').extract_first().strip()]
        tag_list.append('中国建筑防水协会')
        tags =",".join(tag_list)
        # # url经过MD5压缩后作为数据表的主键object_id
        # detail_item['object_id'] = get_md5(url)
        # detail_item["title"] = title
        # detail_item["date"] = date
        # detail_item["content"] = content
        # detail_item["tags"] = tags
        # detail_item["table"] = 'association_news'
        #通过ItemLoader加载实例
        item_loader = MyItemLoader(item=detail_item, response=response)
        item_loader.add_xpath("title","//font[@class = 'ttt']/text()")
        item_loader.add_xpath("date","//span[@class='xhjstime']/text()")
        item_loader.add_xpath("content","//div[@class='clearFloat xhp']")

        item_loader.add_value("url",response.url)
        item_loader.add_value("tags",tags)
        item_loader.add_value("object_id",get_md5(response.url))
        detail_item = item_loader.load_item()
        yield detail_item

