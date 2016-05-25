# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/10/20
# @description:

import re
import requests
import traceback
from urlparse import urlparse
from lxml.html import soupparser
from furion.lib.model.site import Site
from furion.lib.model.session import sessionCM
from furion.lib.nosql.mongo_util import FeedsWarehouse
from furion.lib.nosql.redis_util import RedisUtil
from furion.lib.utils.logger_util import logger
from furion.task.crawl_item import crawl_item


class SmtGroup():

    def __init__(self, start_url, user_id):
        self.start_url = start_url
        self.user_id = user_id
        self.page_list = list()
        self.page_set = set()
        self.iid_set = set()
        self.crawl_cookie = ""
        self.cookie_list = RedisUtil("smt_crawl_cookies", RedisUtil.RU_L)
        with sessionCM() as session:
            url_obj = urlparse(start_url)
            self.site = Site.find_by_netloc(session, url_obj.netloc)
        self.feed_entry = FeedsWarehouse("fb" + str(user_id))

    @classmethod
    def validate_url(cls, url):
        if "?" in url:
            url = url.split("?")[0]
        ss_str = "http://www\.aliexpress\.com/store/group/.+/[\d_]+\.html"
        if re.compile(ss_str).match(url):
            return True
        else:
            return False

    def extract_page(self, dom):
        page_content = dom.find(".//div[@class='ui-pagination-navi util-left']")
        pages = page_content.findall(".//a")
        pages = [page.get("href") for page in pages]
        for page in pages:
            if page in self.page_set:
                continue
            self.page_set.add(page)
            self.page_list.append(page)

    def extract_url(self, dom):
        item_contents = dom.findall(".//div[@class='detail']/h3/a")
        for item in item_contents:
            url = item.get("href")
            if url in self.iid_set:
                continue
            self.iid_set.add(url)
            crawl_item.delay(url, self.user_id, "AliExpress", self.site)

    def get_page_content(self):
        try_times = 0
        proxy = None
        headers = {
            'Cookie': self.crawl_cookie
        }
        logger.info(headers)
        while try_times < 5:
            try:
                if not proxy:
                    res = requests.get(self.start_url, timeout=10, headers=headers)
                else:
                    res = requests.get(self.start_url, proxy={"http": proxy}, timeout=10)
                return res.text
            except Exception, e:
                logger.info(e.message)
                try_times += 1

    def start_extract(self):
        page = 1
        self.crawl_cookie = self.cookie_list.get()
        cookie_expired = False
        while True:
            logger.info(self.start_url)
            logger.info("正在抓取第%d页" % page)
            content = self.get_page_content()
            dom = soupparser.fromstring(content)
            self.extract_url(dom)
            try:
                self.extract_page(dom)
            except Exception, e:
                cookie_expired = True
                self.crawl_cookie = self.cookie_list.get()
                logger.warning(traceback.format_exc(e))
            if len(self.page_list) == 0:
                break
            self.start_url = self.page_list.pop()
            page += 1
        if not cookie_expired:
            self.cookie_list.set(self.crawl_cookie)
