# -*- coding: utf-8 -*-

# Define here the models for your spider middleware
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/spider-middleware.html

from scrapy import signals
from fake_useragent import UserAgent
import  random

class SshspiderSpiderMiddleware(object):
    # Not all methods need to be defined. If a method is not defined,
    # scrapy acts as if the spider middleware does not modify the
    # passed objects.

    @classmethod
    def from_crawler(cls, crawler):
        # This method is used by Scrapy to create your spiders.
        s = cls()
        crawler.signals.connect(s.spider_opened, signal=signals.spider_opened)
        return s

    def process_spider_input(self, response, spider):
        # Called for each response that goes through the spider
        # middleware and into the spider.

        # Should return None or raise an exception.
        return None

    def process_spider_output(self, response, result, spider):
        # Called with the results returned from the Spider, after
        # it has processed the response.

        # Must return an iterable of Request, dict or Item objects.
        for i in result:
            yield i

    def process_spider_exception(self, response, exception, spider):
        # Called when a spider or process_spider_input() method
        # (from other spider middleware) raises an exception.

        # Should return either None or an iterable of Response, dict
        # or Item objects.
        pass

    def process_start_requests(self, start_requests, spider):
        # Called with the start requests of the spider, and works
        # similarly to the process_spider_output() method, except
        # that it doesn’t have a response associated.

        # Must return only requests (not items).
        for r in start_requests:
            yield r

    def spider_opened(self, spider):
        spider.logger.info('Spider opened: %s' % spider.name)

class RandomUserAgentMiddleware(object):
    #随机更换user-agent
    def __init__(self,crawler):
        super(RandomUserAgentMiddleware,self).__init__()
        self.ua = UserAgent()
        self.ua_type = crawler.settings.get('RANDOM_UA_TYPE','random')

    @classmethod
    def from_crawler(cls,crawler):
        return cls(crawler)

    def process_request(self,request,spider):
        def get_ua():
            return getattr(self.ua,self.ua_type)

        request.headers.setdefault('User-Agent',get_ua())

class RandomProxyMiddleware(object):
    def process_request(self,request,spider):
        def get_random():
            p_list = ["http://61.135.217.7:80",
                      "http://58.208.247.208:8118",
                      "http://113.116.159.217:53281",
                      "http://120.25.164.134:8118",
                      "http://121.204.165.71:8118",
                      "http://122.156.211.138:80",
                      "http://171.38.42.174:8123",
                      "http://101.68.73.54:53281",
                      "http://119.29.178.21:8118",
                      "http://117.78.37.198:8000",
                      "http://182.90.14.168:80",
                      "http://114.115.216.99:80",]
            index = random.randint(0,len(p_list)-1)
            return p_list[index]

        request.meta["proxy"] = get_random()
