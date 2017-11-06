# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from scrapy.loader import ItemLoader
from lxml import etree

#爬取网站：中国国际招标网
#爬取内容 工程信息
from sshSpider.utils.common import get_md5
from sshSpider.items import ChinaBiddingItem,MyItemLoader
import re
class ChinabiddingspiderSpider(scrapy.Spider):
    name = 'chinabiddingSpider'
    allowed_domains = ['http://www.chinabidding.com']
    start_urls = [
        'http://www.chinabidding.com/search/proj.htm?poClass=BidResult&infoClassCodes=0108&fullText=防水工程&pubDate=3&currentPage=1',
                  'http://www.chinabidding.com/search/proj.htm?poClass=BidResult&infoClassCodes=0108&fullText=堵漏工程&pubDate=3&currentPage=1',
                  'http://www.chinabidding.com/search/proj.htm?poClass=BidResult&infoClassCodes=0108&fullText=建筑工程&pubDate=3&currentPage=1',
                  'http://www.chinabidding.com/search/proj.htm?poClass=BidResult&infoClassCodes=0108&fullText=市政工程&pubDate=3&currentPage=1',
                  'http://www.chinabidding.com/search/proj.htm?poClass=BidResult&infoClassCodes=0108&fullText=高速工程&pubDate=3&currentPage=1',
                  'http://www.chinabidding.com/search/proj.htm?poClass=BidResult&infoClassCodes=0108&fullText=公路工程&pubDate=3&currentPage=1',
                  'http://www.chinabidding.com/search/proj.htm?poClass=BidResult&infoClassCodes=0108&fullText=地铁工程&pubDate=3&currentPage=1',
                  'http://www.chinabidding.com/search/proj.htm?poClass=BidResult&infoClassCodes=0108&fullText=隧道工程&pubDate=3&currentPage=1',
                  'http://www.chinabidding.com/search/proj.htm?poClass=BidResult&infoClassCodes=0108&fullText=装修&pubDate=3&currentPage=1'
        # 'http://www.chinabidding.com/bidDetail/231372291-BidResult.html'
                  ]
    #爬取列表页
    def parse(self, response):
        #1爬取当前页的列表信息
        li_list = response.xpath("//ul[@class='as-pager-body']/li")
        for li in li_list:
            url = li.xpath('a[@class="as-pager-item"]/@href').extract_first()  # 当前页工程详情的url列表
            tags = li.xpath("a/div/dl/dd/span[1]/strong/text()").extract_first()  # 工程分类列表
            location = li.xpath("a/div/dl/dd/span[2]/strong/text()").extract_first()  # 工程所属位置列表
            yield Request(url=url,meta={"tags":tags,"location":location},callback=self.parse_detail,dont_filter=True,method='POST')
        #2爬取下一页
        next_page = response.xpath("//a[contains(text(),'下一页')]/@onclick").extract_first()
        if next_page:
            match = re.search('(\d+)',next_page)
            if match:
                next_page = match.group()
                next_url = re.sub('currentPage=(\d+)','currentPage='+next_page,response.url,0)
                yield Request(url=next_url,callback=self.parse,dont_filter=True,method='POST')


    #爬取详情页
    def parse_detail(self, response):
        #通过item_loader加载item
        detail_item = ChinaBiddingItem()
        tags = response.meta.get("tags","")
        location = response.meta.get("location","")
        item_loader = MyItemLoader(item=detail_item, response=response)
        if tags == None:
            tags= [tags,"中国国际招标网"]
        else:
            tags= [tags,"中国国际招标网"]
        item_loader.add_value("tags",tags)
        item_loader.add_value("location",[location])
        item_loader.add_value("object_id",get_md5(response.url))
        item_loader.add_value("url",response.url)

        item_loader.add_xpath("date","//active[@class='title']/em/text()|//div[@class='as-article']/p/span/text()")
        item_loader.add_xpath("title","//active[@class='title']/h1/text()|//div[@class='as-article']/h3/text()")
        item_loader.add_xpath("content","//section[@class='text']|//div[@class='as-article-body table-article']")
        detail_item = item_loader.load_item()
        yield detail_item
