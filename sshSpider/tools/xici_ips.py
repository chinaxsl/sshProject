import requests
from scrapy.selector import Selector

#爬取西刺的免费ip代理
def crawl_ips():
    headers = {"User-Agent":"Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/61.0.3163.100 Safari/537.36"}
    re = requests.get("http://www.xicidaili.com/nn/",headers=headers)

    selector = Selector(text=re.text)
    all_trs = selector.css()