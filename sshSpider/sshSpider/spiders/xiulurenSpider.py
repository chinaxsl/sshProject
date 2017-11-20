# -*- coding: utf-8 -*-
import scrapy

from urllib import parse
from scrapy.http import Request
from sshSpider.items import NewsItem,MyItemLoader
from sshSpider.utils.common import get_md5


#爬取网站：杭州修路人官网
#爬取信息：新闻动态
class XiulurenspiderSpider(scrapy.Spider):
    name = 'xiulurenSpider'
    allowed_domains = ['http://www.hzup.com']
    start_urls = ['http://www.hzup.com/c_news']
    #爬取列表页
    def parse(self, response):
        url_list = response.xpath("//div[@class='n_news_list']/a[2]/@href").extract()
        for url in url_list:
            yield Request(url=parse.urljoin(response.url,url),callback=self.parse_detail,dont_filter=True)
        next_url = response.xpath("//div[@id='page']//*[contains(text(),'下一页')]/@href").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse,dont_filter=True)

    #爬取详情页
    def parse_detail(self,response):
        # title = response.xpath("//div[@class='show_n_title']/strong/text()").extract_first()
        # date = response.xpath("//div[@class='show_n_c']/text()").extract_first().strip()
        # match = re.search('(\d{4}\-\d{1,2}\-\d{1,2})',date)
        # if match:
        #     date = match.group()
        # else:
        #     date = None
        # try:
        #     date = datetime.datetime.strptime(date, "%Y/%m/%d").date()
        # except Exception as e:
        #     date = datetime.datetime.now().date()
        # content = response.xpath("//div[@class='show_n_content']").extract_first()
        # url = response.url
        detail_item = NewsItem()
        tag_list = []
        tag_list.append('杭州修路人')
        tags =",".join(tag_list)
        # url经过MD5压缩后作为数据表的主键object_id
        # detail_item['object_id'] = get_md5(url)
        # detail_item["title"] = title
        # detail_item["date"] = date
        # detail_item["content"] = content
        # detail_item["tags"] = tags
        # detail_item["table"] = "xiuluren_news"
        #通过ItemLoader加载实例
        item_loader = MyItemLoader(item=detail_item, response=response)
        item_loader.add_xpath("title","//div[@class='show_n_title']/strong/text()")
        item_loader.add_xpath("date","//div[@class='show_n_c']/text()")
        item_loader.add_xpath("content","//div[@class='show_n_content']")

        item_loader.add_value("url", response.url)
        item_loader.add_value("tags",tags)
        item_loader.add_value("object_id",get_md5(response.url))
        detail_item = item_loader.load_item()
        yield detail_item
