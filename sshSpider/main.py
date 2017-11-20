# -*- coding: utf-8 -*-

from scrapy.cmdline import execute

import sys
import os

sys.path.append(os.path.dirname(os.path.abspath(__file__)))
# execute(["scrapy", "crawl", "xiulurenSpider"])
# execute(["scrapy", "crawl", "cnwbSpider"])
execute(["scrapy", "crawl", "chinabiddingSpider"])
# execute(["scrapy", "crawl", "zgszSpider"])
# execute(["scrapy", "crawl", "bmlinkSpider"])