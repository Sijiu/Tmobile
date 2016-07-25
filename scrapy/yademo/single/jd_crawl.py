# -*- coding: utf-8 -*-

# !/usr/bin/python
# @author: xuhe
# @date: 15/6/17
# @description:


import json
import traceback
import re
import requests
from urllib import urlencode
from furion.lib.handlers.template import generate_template
from furion.lib.utils.logger_util import logger
from furion.lib.utils.currency_util import transform


class JdLink(object):

    def __init__(self, url):
        self.url = url
        self.item_id = self._extract_id()
        self.content = self._ready()
        self.product = generate_template()

    def _extract_id(self):
        zz_str = r"/(\d+)\.html"
        pattern = re.compile(zz_str)
        result = pattern.findall(self.url)
        return result[0]

    @property
    def source_info(self):
        return dict(
            SiteID="",
            Site="",
            Platform="JD",
            Link=self.url,
            ProductID=self.item_id
        )

    def _ready(self):
        try_times = 0
        headers = {
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Host": "item.jd.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36",
        }
        while try_times < 5:
            try:
                try_times += 1
                res = requests.get(self.url, headers=headers, timeout=10)
                return res.text
            except Exception, e:
                logger.error(traceback.format_exc(e))
        raise Exception

    def _title(self):
        zz_str = "<div id=\"itemInfo\">\s+<div id=\"name\">\s+<h1>(.+?)</h1>"
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        if not result:
            raise Exception
        return result[0]

    def _product_specifics(self):
        zz_str = '(<ul id="parameter2"[\s\S]+?</ul>)'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        result = result[0].strip()

        ss_str = " <li title='[\s\S]+?'>([\s\S]+?)</li>"
        pattern = re.compile(ss_str)
        result = pattern.findall(result)
        if result:
            result = result[4:]
            return result
        else:
            return ""

    def _start_price(self):
        zz_str = 'product: {\s*skuid: (\d+),'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        sku_id = result[0].strip()
        return self._get_price(sku_id)

    def _package_info(self):
        pass

    def _keywords(self):
        pass

    def _bullet_points(self):
        pass

    def _pictures(self):
        zz_str = '(<div id="spec-list"[\s\S]+?</div>)'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        result = result[0].strip()
        if not result:
            return list()
        ss_str = "src='([\s\S]+?)'"
        pattern = re.compile(ss_str)
        result = pattern.findall(result)
        return result

    def _product_unit(self):
        pass

    def _product_sku(self):
        zz_str = 'colorSize: (\[[\s\S]+?\]),'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        if not result:
            return list()
        sku_str = result[0].strip()
        multi_sku = json.loads(sku_str)
        variations = list()

        for sku in multi_sku:
            vs = list()
            price = self.product["StartPrice"]
            for key, value in sku.iteritems():
                if key == "SkuId":
                    price = self._get_price(value) or price
                    continue
                if value == "*":
                    continue
                vs.append({
                    "Name": key,
                    "Value": value,
                    "NameID": "",
                    "ValueID": "",
                    "Image": []
                })
            variations.append({
                "Stock": 999,
                "SKU": "",
                "Price": price,
                "SkuID": "",
                "VariationSpecifics": vs
            })
        return variations

    @staticmethod
    def _get_price(sku_id):
        url = "http://p.3.cn/prices/get"
        params = {"skuid": "J_%s" % sku_id}
        url = "?".join([url, urlencode(params)])
        res = requests.get(url)
        try:
            res_dict = res.json()
            return res_dict[0].get("p")
        except Exception, e:
            logger.warning(traceback.format_exc(e))
            return 0

    def _specifics(self):
        zz_str = '<ul id="parameter2" class="p-parameter-list">([\s\S]+?)</ul>'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        result = result[0].strip()

        ss_str = '<li title=.+?>(.+?)</li>'
        pattern = re.compile(ss_str)
        sps = pattern.findall(result)

        specifics = []
        gross_weight = sps[4].split(u"：")[1].strip()
        if gross_weight.endswith("kg"):
            gross_weight = "%.2f" % float(gross_weight.replace("kg", ""))
        elif gross_weight.endswith("g"):
            gross_weight = gross_weight.replace("g", "")
            gross_weight = "%.2f" % (float(gross_weight)/1000)
        else:
            gross_weight = ""
        for sp in sps[5:]:
            key, value = sp.split(u"：")
            specifics.append({
                "Name": key.strip(),
                "NameID": "",
                "Value": value.strip(),
                "ValueID": ""
            })
        return {
            "ProductSpecifics": specifics,
            "GrossWeight": gross_weight
        }

    def _description(self):
        desc_url = "http://d.3.cn/desc/%s?callback=showdesc" % self.source_info["ProductID"]
        res = requests.get(desc_url)
        res_text = res.text[9:-1]
        desc_dict = json.loads(res_text)
        desc_text = re.sub("[\n\r\t]", " ", desc_dict["content"])
        return desc_text.replace("data-lazyload", "src")

    def _category(self):
        pass

    def _extract_value(self):
        pass

    def export_product(self):
        self.product["Title"] = self._title()
        self.product["Description"] = self._description()
        self.product["PictureURLs"] = self._pictures()
        self.product.update(self._specifics())
        self.product["StartPrice"] = self._start_price()
        self.product["SourceInfo"] = self.source_info
        self.product["ProductSKUs"] = self._product_sku()
        return self.product
