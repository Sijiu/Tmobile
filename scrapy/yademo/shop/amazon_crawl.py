# -*- coding=utf-8 -*-

"""
@author:yangguoli
@date:2015/07/01
@version:
@description:
"""
import re
import requests
import ujson as json
from urlparse import urlparse
from furion.lib.model.session import sessionCM
from furion.lib.model.site import Site
from furion.lib.nosql.mongo_util import FeedsWarehouse
from furion.lib.utils.amazon_shop import SHOP_CRAWL
from furion.lib.utils.logger_util import logger
from furion.task.crawl_item import crawl_item


class AmazonCrawl(object):

    def __init__(self, start_url, user_id):
        self.start_url = start_url
        self.user_id = user_id
        self.page_list = list()
        url_obj = urlparse(start_url)
        with sessionCM() as session:
            self.site = Site.find_by_netloc(session, url_obj.netloc)
        self.feed_entry = FeedsWarehouse("fb" + str(user_id))

    @classmethod
    def validate_url(cls, url):
        if re.match(r"http://www.amazon(.com|.co.uk|.ca)/gp/aag/main\?\S*seller=\S*", url):
            return True
        elif re.match(r"http://www.amazon.com/sp?\S*?seller=\S*", url):
            return True
        else:
            return False

    def get_page_content(self, seller, page, source):
        headers = SHOP_CRAWL[source]["headers"]
        url = SHOP_CRAWL[source]["url"]
        try_times = 5
        while try_times > 0:
            try:
                res = requests.post(
                    url, headers=headers,
                    data={"seller": seller, "currentPage": page, "useMYI": 0},
                )
                return res.text
            except Exception, e:
                logger.error(e.message)
                try_times -= 1
        return None

    def extract_url(self, source):
        for code in self.page_list:
            logger.info("*" * 10)
            url = source + "/dp/%s" % str(code)
            if self.feed_entry.get({"SourceInfo.ProductID": code}):
                continue
            crawl_item.delay(url, self.user_id, "Amazon", self.site)

    def start_extract(self):
        current_page = 1
        seller = re.findall(r'seller=([\w]+)', self.start_url)[0]
        logger.info(self.start_url)
        source_temp = re.findall(r"(\S+?)/gp", self.start_url)
        if not source_temp:
            source_temp = re.findall(r"(\S+?)/sp?", self.start_url)
        source = source_temp[0]
        while True:
            content = self.get_page_content(seller, current_page, source)
            try:
                code_list = json.loads(content)
                if not code_list:
                    break
                self.page_list.extend(code_list)
                current_page += 1
            except Exception:
                break
        self.extract_url(source)