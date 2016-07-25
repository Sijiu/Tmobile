# !/usr/bin/python
# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/6/30
# @description:


import re
import requests
from urlparse import urlparse
from furion.lib.model.session import sessionCM
from furion.lib.model.site import Site
from furion.lib.nosql.mongo_util import FeedsWarehouse
from furion.lib.utils.logger_util import logger
from furion.task.crawl_item import crawl_item


class EbayCrawl(object):

    def __init__(self, start_url, user_id):
        self.start_url = start_url
        self.user_id = user_id
        self.page_list = list()
        self.page_set = set()
        self.iid_set = set()
        url_obj = urlparse(start_url)
        with sessionCM() as session:
            self.site = Site.find_by_netloc(session, url_obj.netloc)
        self.feed_entry = FeedsWarehouse("fb" + str(user_id))

    @classmethod
    def validate_url(cls, url):
        zz_str = "http://www\.ebay\.[\.a-z]+/sch/[\w\d-]+/m\.html"
        ss_str = "http://www\.ebay\.[\.a-z]+/sch/m\.html\?.*_ssn=[\w\d-]+"
        if re.compile(zz_str).match(url) \
                or re.compile(ss_str).match(url):
            return True
        else:
            return False

    def extract_url(self, content):
        zz_str = r'<ul id="ListViewInner">([\s\S]+)</ul>[\s\S]+?</w-root>'
        pattern = re.compile(zz_str)
        result = pattern.findall(content)
        if not result:
            return
        id_str = r'<a href="(.+?)" class="img imgWr2'
        pattern = re.compile(id_str)
        urls = pattern.findall(result[0])
        for url in urls:
            if url in self.iid_set:
                continue
            logger.info(url)
            self.iid_set.add(url)
            crawl_item.delay(url, self.user_id, "eBay", self.site)
        logger.info("*" * 40)

    def extract_page(self, content):
        zz_str = r'<td class="pages"([\s\S]+?)</td>'
        pattern = re.compile(zz_str)
        result = pattern.findall(content)
        if not result:
            return
        id_str = r'<a.+?class="pg " href="(.+?)" *>\d+</a>'
        pattern = re.compile(id_str)
        urls = pattern.findall(result[0])
        for url in urls:
            if "_pgn" not in url or url in self.page_set:
                continue
            self.page_list.append(url)
            self.page_set.add(url)

    def get_page_content(self):
        try_times = 0
        proxy = None
        headers = {}
        while try_times < 5:
            try:
                if not proxy:
                    res = requests.get(self.start_url, timeout=10)
                else:
                    res = requests.get(self.start_url, proxy={"http": proxy}, timeout=10)
                logger.info("success to get the page content")
                return res.text
            except Exception, e:
                logger.info(e.message)
                try_times += 1

    def start_extract(self):
        page = 1
        self.page_set.add(self.start_url)
        while True:
            logger.info(self.start_url)
            logger.info("Is grabbing the page of %d" % page)
            content = self.get_page_content()
            self.extract_url(content)
            self.extract_page(content)
            if len(self.page_list) == 0:
                break
            self.start_url = self.page_list.pop()
            page += 1