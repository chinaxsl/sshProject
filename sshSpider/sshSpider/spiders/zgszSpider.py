# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from sshSpider.utils.common import get_md5
from urllib import parse
from sshSpider.items import MyItemLoader,NewsItem


#爬取网站 中国市政协会官网
#爬取信息 协会动态
class ZgszspiderSpider(scrapy.Spider):
    name = 'zgszSpider'
    allowed_domains = ['http://www.zgsz.org.cn/']
    start_urls = ['http://www.zgsz.org.cn/zytz/index_9.html']


    #爬取列表页
    def parse(self, response):
        url_list = response.xpath("//ul[@class='item_list']/li/a/@href").extract()
        for url in url_list:
            yield Request(url=parse.urljoin(response.url, url), callback=self.parse_detail, dont_filter=True)
        next_url = response.xpath("//div[@class='pageCount']/a[contains(text(),'下一页')]/@href").extract_first()
        next_url = parse.urljoin(response.url, next_url)
        if next_url!=response.url:
            yield Request(url=next_url, callback=self.parse, dont_filter=True)

    # 爬取详情页
    def parse_detail(self, response):

        detail_item = NewsItem()
        tags = "中国市政协会"
        item_loader = MyItemLoader(item=detail_item, response=response)
        item_loader.add_xpath("title", "//h2[@class='article_title']/text()")
        item_loader.add_xpath("date", "//div[@class='article_info']/text()")
        item_loader.add_xpath("content", "//div[@class='article_doc']")

        item_loader.add_value("tags", [tags])
        item_loader.add_value("object_id", get_md5(response.url))
        item_loader.add_value("url",response.url)
        detail_item = item_loader.load_item()
        yield detail_item
