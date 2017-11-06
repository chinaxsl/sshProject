# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html
import re
import scrapy
from scrapy.loader import ItemLoader
from scrapy.loader.processors import MapCompose,TakeFirst,Join
import datetime


class SshspiderItem(scrapy.Item):
    # define the fields for your item here like:
    # name = scrapy.Field()
    pass


#正则表达式匹配日期并转换为Date类型
def date_convert(value):
    match = re.search('(\d{4}(/|-)\d{1,2}(/|-)\d{1,2})', value.strip())
    if match:
        date = match.group()
        date = date.replace('/','-',3)
    else:
        date = None
    try:
        date = datetime.datetime.strptime(date, "%Y-%m-%d").date()
    except Exception as e:
        date = datetime.datetime.now().date()
    return date


def handle_contact(value):
    try:
        result = value.split('：')[1]
    except:
        result = value
    return result



def handle_tags(value):
    if value!=None:
        value = value.replace(':',',')
    return value


class MyItemLoader(ItemLoader):
    #自定义itemloader
    default_output_processor = TakeFirst()


#协会item
class NewsItem(scrapy.Item):
    title = scrapy.Field()
    date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    tags = scrapy.Field(
        output_processor=Join(',')
    )
    content = scrapy.Field()
    object_id = scrapy.Field()
    url = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = "insert into association_news(object_id,title,content,date,tags,url) Value(%s,%s,%s,%s,%s,%s)"
        params = (self['object_id'],self['title'],self['content'],self['date'],self['tags'],self['url'])
        return insert_sql,params


#杭州修路人网item
class XiuLuRenItem(NewsItem):
    def get_insert_sql(self):
        insert_sql = "insert into xiuluren_news(object_id,title,content,date,tags,url) Value(%s,%s,%s,%s,%s.%s)"
        params = (self['object_id'], self['title'], self['content'], self['date'], self['tags'],self['url'])
        return insert_sql, params


#中国国际投标网item
class ChinaBiddingItem(scrapy.Item):
    location = scrapy.Field()
    title = scrapy.Field()
    date = scrapy.Field(
        input_processor=MapCompose(date_convert)
    )
    tags = scrapy.Field(
        input_processor=MapCompose(handle_tags)
    )
    content = scrapy.Field()
    object_id = scrapy.Field()
    url = scrapy.Field()

    def get_insert_sql(self):
        insert_sql = "insert into project(object_id,title,content,date,tags,location,url) Value(%s,%s,%s,%s,%s,%s,%s)"
        params = (self['object_id'], self['title'], self['content'], self['date'], self['tags'],self['location'],self['url'])
        return insert_sql, params


#企业item
class CompanyItem(scrapy.Item):
    company_name = scrapy.Field()
    company_product = scrapy.Field()
    company_introduction = scrapy.Field()
    company_model = scrapy.Field()
    company_contact_person = scrapy.Field()
    company_contact_mobilephone = scrapy.Field(
        input_processor = MapCompose(handle_contact)
    )
    company_contact_telephone = scrapy.Field(
        input_processor = MapCompose(handle_contact)
    )
    company_faxnumber = scrapy.Field(
        input_processor=MapCompose(handle_contact)
    )
    company_detailed_location = scrapy.Field(
        input_processor=MapCompose(handle_contact)
    )
    company_main_industry = scrapy.Field(
    )
    company_type = scrapy.Field(
    )
    from_website = scrapy.Field()
    object_id = scrapy.Field()
    url = scrapy.Field()

    def get_insert_sql(self):
        params_list = ['object_id', 'company_name', 'company_product', 'company_introduction',
                  'company_model', 'company_contact_person', 'company_contact_mobilephone',
                  'company_contact_telephone','company_faxnumber','company_detailed_location',
                  'company_main_industry','company_type','from_website','url']
        for para in params_list:
            try:
                self[para] is None
            except:
                self[para] = '暂无'
        insert_sql = """insert into company(object_id,company_name,company_product,company_introduction,company_model,
        company_contact_person,company_contact_mobilephone,company_contact_telephone,company_faxnumber,
        company_detailed_location,company_main_industry,company_type,from_website,url)
        Value(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
        params = tuple(self[para] for para in params_list)
        return insert_sql, params



