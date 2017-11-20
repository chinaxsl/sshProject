# -*- coding: utf-8 -*-
import scrapy
from scrapy.http import Request
from sshSpider.items import CompanyItem,MyItemLoader
from sshSpider.utils.common import get_md5
from urllib import parse

#  爬取网站 ： 中国建材网
# 爬取内容：公司信息
class BmlinkspiderSpider(scrapy.Spider):
    name = 'bmlinkSpider'
    allowed_domains = ['http://www.bmlink.com']
    start_urls = [
        # 'http://www.bmlink.com/company/search/p1-bm8.html?key=%b7%c0%cb%ae',
        # 'http://www.bmlink.com/supply/list-bm8.html?key=%b6%c2%c2%a9%b9%ab%cb%be',
        # 'http://www.bmlink.com/supply/list-bm8.html?key=%bd%a8%d6%fe',
        'http://www.bmlink.com/supply/list-bm2.html?key=%bd%a8%d6%fe',
        'http://www.bmlink.com/supply/list-bm8.html?key=%d7%b0%d0%de%b9%ab%cb%be',
        'http://www.bmlink.com/supply/list-bm8.html?key=%cb%ed%b5%c0',
        'http://www.bmlink.com/supply/list-bm8.html?key=%b5%d8%cc%fa'
    ]

    def parse(self, response):
        companies = response.xpath("//div[@class='info']")
        for company in companies:
            detail_url = company.xpath("p/a/@href").extract_first()
            yield Request(url=parse.urljoin(response.url,detail_url),callback=self.parse_detail,dont_filter=True)
        #爬取下一页
        next_url = response.xpath("//a[contains(text(),'下一页')]/@href").extract_first()
        if next_url:
            yield Request(url=parse.urljoin(response.url,next_url),callback=self.parse,dont_filter=True)


    # 爬取详情页
    def parse_detail(self, response):
        company_contact_person = response.xpath("//div[@class='rightSider fr']/h3/text()").extract_first()
        company_contact_mobilephone = response.xpath("//div[@class='rightSider fr']/p[@class='iphone']/text()").extract_first()
        company_contact_telephone = response.xpath("//div[@class='rightSider fr']/p[@class='tel']/text()").extract_first()
        company_faxnumber = response.xpath("//div[@class='rightSider fr']/p[@class='fax']/text()").extract_first()
        company_detailed_location = response.xpath("//div[@class='rightSider fr']/p[@class='area']/text()").extract_first()
        detail = response.xpath("//a[@class='m-more']/@href").extract_first()
        meta = {"company_contact_person":company_contact_person,
                "company_contact_mobilephone":company_contact_mobilephone,
                "company_contact_telephone":company_contact_telephone,
                "company_faxnumber":company_faxnumber,
                "company_detailed_location":company_detailed_location}
        #删除字典中的空的键值对
        empty = []
        for i in meta.keys():
            if meta[i]==None:
                empty.append(i)
        for e in empty:
            del(meta[e])

        yield Request(url=parse.urljoin(response.url,detail),callback=self.parse_more,meta=meta,dont_filter=True)

    # 爬取更多详细信息
    def parse_more(self,response):
        detail_item = CompanyItem()
        from_website = "中国建材网"
        company_contact_person = response.meta.get("company_contact_person","暂无")
        company_contact_mobilephone = response.meta.get("company_contact_mobilephone", "暂无")
        company_contact_telephone = response.meta.get("company_contact_telephone", "暂无")
        company_faxnumber = response.meta.get("company_faxnumber", "暂无")
        company_detailed_location = response.meta.get("company_detailed_location", "暂无")
        item_loader = MyItemLoader(item=detail_item, response=response)
        item_loader.add_xpath("company_product", "//div[@class='head-product']/strong/text()")
        item_loader.add_xpath("company_name", "//div[@class='head-product']/h2/text()")
        item_loader.add_xpath("company_introduction", "//div[@class='detail']")
        item_loader.add_xpath("company_model","//ul[@class='tableType']/li[3]/p[2]/text()")
        item_loader.add_xpath("company_main_industry","//ul[@class='tableType']/li[4]/p[2]/text()")
        item_loader.add_xpath("company_type", "//ul[@class='tableType']/li[2]/p[2]/text()")

        item_loader.add_value("from_website",from_website)
        item_loader.add_value("company_contact_person", company_contact_person)
        item_loader.add_value("company_contact_mobilephone", company_contact_mobilephone)
        item_loader.add_value("company_contact_telephone", company_contact_telephone)
        item_loader.add_value("company_faxnumber", company_faxnumber)
        item_loader.add_value("company_detailed_location", company_detailed_location)
        item_loader.add_value("object_id", get_md5(response.url))
        item_loader.add_value("url", response.url)
        detail_item = item_loader.load_item()
        try:
            detail_item['company_type']
        except:
            detail_item['company_type'] = '暂无'
        yield detail_item
