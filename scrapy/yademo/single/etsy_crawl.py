# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/12/1
# @description: 


import re
import requests
import traceback
from itertools import product
from furion.lib.handlers.template import generate_template
from furion.lib.utils.logger_util import logger


class EtsyLink(object):

    def __init__(self, url):
        self.url = url
        self.item_id = self._extract_id()
        self.content = self._ready()
        self.product = generate_template()

    def _extract_id(self):
        zz_str = r"listing/(\d+)/"
        pattern = re.compile(zz_str)
        result = pattern.findall(self.url)
        if not result:
            raise Exception
        return result[0]

    @property
    def source_info(self):
        return dict(
            SiteID="",
            Site="",
            Platform="Etsy",
            Link=self.url,
            ProductID=self.item_id
        )

    def _ready(self):
        try_times = 0
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Encoding": "gzip,deflate,sdch",
            "Accept-Language": "zh-CN,zh;q=0.8:",
            "Cache-Control": "max-age=0:",
            "Connection": "keep-alive",
            "Cookie": "ua=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgNi4xOyBXT1c2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzI4LjAuMTUwMC43MiBTYWZhcmkvNTM3LjM2; user_prefs=1&2596706699&q0tPzMlJLaoEAA==; perf=wf:1; ua=TW96aWxsYS81LjAgKFdpbmRvd3MgTlQgNi4xOyBXT1c2NCkgQXBwbGVXZWJLaXQvNTM3LjM2IChLSFRNTCwgbGlrZSBHZWNrbykgQ2hyb21lLzI4LjAuMTUwMC43MiBTYWZhcmkvNTM3LjM2; last_browse_page=https%3A%2F%2Fwww.etsy.com%2Fshop%2FBannorToys; fve=1448877263.0; _ga=GA1.2.762151047.1448877196; _dc_gtm_UA-2409779-1=1; uaid=uaid%3DB5tWO8JKJFIDwoy1Qa5XJRlld3uO%26_now%3D1448881932%26_slt%3DxIyJu90m%26_kid%3D1%26_ver%3D1%26_mac%3DyAs3hF6l_A3oS_ZjeWM5OjwkMIHwzfqhlJfwmzeNCi8.; RT=sl=0&ss=1448878424009&tt=0&obo=0&bcn=%2F%2F36fb607e.mpstat.us%2F&sh=&dm=etsy.com&si=f437d3b7-63b6-484e-9b6c-4ff2fb034c2f&r=https%3A%2F%2Fwww.etsy.com%2Flisting%2F247124492%2Fwish-bracelet-set-of-2-hearts-locked&ul=1448881947305",
            "Host": "www.etsy.com",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/28.0.1500.72 Safari/537.36",
        }
        while try_times < 5:
            try:
                try_times += 1
                res = requests.get(self.url, timeout=10)
                return res.text
            except Exception, e:
                logger.error(traceback.format_exc(e))
        raise Exception

    def _title(self):
        zz_str = 'itemprop="name">(.+?)<'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        if not result:
            raise Exception
        return result[0]

    def _product_specifics(self):
        pass

    def _start_price(self):
        zz_str = '<span class="currency-value">([\d\.]+)</span>'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        return result[0] if result else ""

    def _package_info(self):
        pass

    def _keywords(self):
        pass

    def _bullet_points(self):
        pass

    def _pictures(self):
        zz_str = 'data-full-image-href="(.+?)"'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        return result

    def _product_unit(self):
        pass

    @staticmethod
    def _find_price(content):
        zz_str = "\[\$([\d\.]+?)\]"
        pattern = re.compile(zz_str)
        result = pattern.findall(content)
        if not result:
            return 0
        return result[0].strip()

    @staticmethod
    def _del_price(content):
        zz_str = "(.+?)[\[|]"
        pattern = re.compile(zz_str)
        result = pattern.findall(content)
        if not result:
            return 0
        return result[0].strip()

    def _product_sku(self):
        zz_str = 'item-variation-option clear([\s\S]+?)</div>'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        if not result:
            return list()
        sku_list = list()
        for sku in result:
            cell = list()
            zz_str = '<label class="[\s\S]+?">(.+?)</label>'
            pattern = re.compile(zz_str)
            name = pattern.findall(sku)[0].strip()
            zz_str = '<option *value="\d+">\s+(.+?)\s+</option'
            pattern = re.compile(zz_str)
            value_list = pattern.findall(sku)
            for value in value_list:
                cell.append([name, value])

            sku_list.append(cell)
        variations = list()
        price = 0
        for r in product(*sku_list):
            vs = list()
            for cell in r:
                if price == 0:
                    var_price = self._find_price(cell[1])
                    if var_price != 0:
                        cell[1] = self._del_price(cell[1])
                        price = var_price

                vs.append({
                    "Name": cell[0],
                    "Value": cell[1],
                    "NameID": "",
                    "ValueID": "",
                    "Image": []
                })
            if price == 0:
                price = self._start_price()
            variations.append({
                "Stock": 999,
                "SKU": "",
                "Price": price,
                "SkuID": "",
                "VariationSpecifics": vs
            })
        return variations

    def _specifics(self):
        pass

    def _description(self):
        zz_str = '<div id="description-text">([\s\S]+?)</div>'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        return result[0].strip() if result else ""

    def _category(self):
        pass

    def _extract_value(self):
        pass

    def export_product(self):
        self.product["Title"] = self._title()
        self.product["Description"] = self._description()
        self.product["PictureURLs"] = self._pictures()
        self.product["StartPrice"] = self._start_price()
        self.product["SourceInfo"] = self.source_info
        self.product["ProductUnit"] = u'100000015'
        self.product["ProductSKUs"] = self._product_sku()
        return self.product