# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/6/30
# @description:


import re
import requests
import lxml.html.soupparser as soupparser
from furion.lib.nosql.mongo_util import FeedsWarehouse
from furion.lib.utils.logger_util import logger
from furion.task.crawl_item import crawl_item


class AliCrawl(object):

    def __init__(self, start_url, user_id):
        self.start_url = start_url
        self.user_id = user_id
        self.page_list = list()
        self.page_set = set()
        self.iid_set = set()
        self.feed_entry = FeedsWarehouse("fb" + str(user_id))

    @classmethod
    def validate_url(cls, url):
        ss_str = "http://\w+\.1688\.com/page/offerlist\.htm.+"
        if re.compile(ss_str).match(url):
            return True
        else:
            return False

    def extract_page(self, dom):
        page_contents = dom.findall(".//li[@class='pagination']/a")
        for page in page_contents:
            url = page.get("href")
            if url.startswith("javascript") or page.get("class") or url in self.page_set:
                continue
            self.page_list.append(url)
            self.page_set.add(url)

    def extract_url(self, dom):
        item_str = ".//ul[@class='offer-list-row']/li/div[@class='image']/a"
        item_contents = dom.findall(item_str)
        for item in item_contents:
            url = item.get("href")
            if url in self.iid_set:
                continue
            self.iid_set.add(url)
            crawl_item.delay(url, self.user_id, "1688")

    def get_page_content(self):
        try_times = 0
        proxy = None
        headers = {
            'Accept': 'text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01',
            'Accept-Encoding': 'gzip, deflate, sdch',
            'Accept-Language': 'en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4',
            'Connection': 'keep-alive',
            'Host': 'detail.1688.com',
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36',
        }
        while try_times < 5:
            try:
                if not proxy:
                    res = requests.get(self.start_url, timeout=10)
                else:
                    res = requests.get(self.start_url, proxy={"http": proxy}, timeout=10)
                return res.text
            except Exception, e:
                logger.info(e.message)
                try_times += 1

    def start_extract(self):
        page = 1
        while True:
            logger.info(self.start_url)
            logger.info("正在抓取第%d页" % page)
            content = self.get_page_content()
            if not content:
                logger.error("1688抓取被屏蔽，连接为%s" % self.start_url)
                break
            dom = soupparser.fromstring(content)
            self.extract_url(dom)
            self.extract_page(dom)
            if len(self.page_list) == 0:
                break
            self.start_url = self.page_list.pop()
            page += 1
