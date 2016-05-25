# -*- coding: utf-8 -*-
# !/usr/bin/python
# @author: xuhe
# @date: 15/6/17
# @description:

import re
import random
import traceback
import requests
import ujson as json
from string import uppercase
from furion.lib.handlers.template import generate_template
from furion.lib.utils.ali_unit import find_by_zh_name
from furion.lib.utils.currency_util import transform


class TaoLink(object):
    def __init__(self, url):
        self.url = url
        self.item_id = self._extract_id()
        self.content = self._ready()
        self.product = generate_template()

    def _extract_id(self):
        tmp = self.url.split("id=")[1]
        tmp2 = tmp.split("&")
        p_id = tmp2[0]
        return p_id

    @property
    def source_info(self):
        return dict(
            SiteID="",
            Site="",
            Platform="Taobao",
            Link=self.url,
            ProductID=self._extract_id()
        )

    def _ready(self):
        try_times = 0
        while try_times < 5:
            try:
                try_times += 1
                res = requests.get(self.url, timeout=10)
                content = res.text
                if isinstance(content, unicode):
                    content = content.encode("utf8")
                return content
            except Exception, e:
                print (traceback.format_exc(e))
        raise Exception

    def _title(self):
        zz_str = "<title>(.+?)-淘宝网</title>"
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        if not result:
            return "标题抓取失败，请联系管理员"
        else:
            return result[0]

    def _description(self):
        zz_str = 'g_config.dynamicScript\(.+?\?\s*[\'\"]//(.+)[\'\"]\s*:[\'\"]//(.+)[\'\"]\)'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        print result
        if not result:
            return "产品描述抓取失败，请联系管理员"
        print "sfdsfsdfs"
        if self.url.startswith("https"):
            desc_req = "https://%s" % result[0][0]
        else:
            desc_req = "http://%s" % result[0][1]
        print desc_req
        desc_res = requests.get(desc_req)
        desc_str = "var desc='(.+?)';"
        pattern = re.compile(desc_str)
        result = pattern.findall(desc_res.text)
        if not result:
            return "产品描述抓取失败，请联系管理员"
        else:
            return result[0]

    def _start_price(self):
        zz_str = '<em class="tb-rmb-num">([ \d\.\-]+)</em>'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        if not result:
            return "0.0"
        else:
            price = result[0].split("-")[0].strip()
            return float(price)
            # return transform("CNY", "USD", float(price))

    def _pictures(self):
        zz_str = "auctionImages\s*:\s*([[\S\s]+?])"
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        if not result:
            return list()
        else:
            images = json.loads(result[0])
            return ["http:%s" % image for image in images]

    def _specifics(self):
        specifics = []
        zz_str = '<ul class="attributes-list">[\s\S]+?</ul>'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        if not result:
            return specifics
        ss_str = '<li title=".+?">(.+?):(?:&nbsp;){0,1}(.+?)</li>'
        pattern = re.compile(ss_str)
        result = pattern.findall(result[0])
        for name, value in result:
            specifics.append({
                "Name": name.strip(),
                "Value": value.strip(),
                "NameID": "",
                "ValueID": ""
            })
        return specifics

    def _product_sku(self):
        zz_str = "skuMap\"{0,1} *: *({[\s\S]+?}\s*})\s*"
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        if not result:
            return list()
        sku_map = json.loads(result[0])
        attr_str = "<ul data-property=\"(.+?)\" class=\"J_TSaleProp([\s\S]+?)</ul>"
        pattern = re.compile(attr_str)
        result = pattern.findall(self.content)
        if not result:
            return list()
        attr_list = list()
        value_str = "<li data-value=\"([\d:]+)\"([\s\S]+?)<span>(.+?)</span>"
        image_str = "background:url\((.+?)\)"
        pattern1 = re.compile(value_str)
        pattern2 = re.compile(image_str)
        for attr_name, attr_text in result:
            value_result = pattern1.findall(attr_text)
            attr_map = dict()
            for attr_id, image, value in value_result:
                image_result = pattern2.findall(image)
                attr_map[attr_id] = {
                    "Name": attr_name,
                    "Value": value,
                    "NameID": "",
                    "ValueID": "",
                    "Image": [self.deal_picture_zoom(image) for image in image_result]
                }
            attr_list.append(attr_map)
        variations = list()
        for result in self.compute_cartesian(attr_list, 0, len(attr_list),
                                             [None]*len(attr_list),
                                             [None]*len(attr_list)):
            key = result.keys()[0]
            value = result[key]
            variations.append({
                "SKU": "",
                "SkuID": "",
                "VariationSpecifics": value,
                "Price": float(sku_map[key]["price"]),
                # "Price": transform("CNY", "USD", float(sku_map[key]["price"])),
                "Stock": sku_map[key]["stock"],
            })
        return variations

    @classmethod
    def gen_parent_sku(cls):
        return "".join([random.choice(uppercase) for i in xrange(10)])

    @classmethod
    def gen_sku_prefix(cls):
        return "".join([random.choice(uppercase) for i in xrange(5)])

    def _product_unit(self):
        zz_str = "J_SpanStock.+?<span>(.+?)\)</span>"
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        zh_name = "" if not result else result[0]
        return find_by_zh_name(zh_name)["code"]

    def compute_cartesian(self, attr_list, start, length, id_list, value_list):
        for nid, ns in attr_list[start].iteritems():
            id_list[start] = nid
            value_list[start] = ns
            if start == length - 1:
                vs = dict()
                vs[";%s;" % (";".join(id_list))] = value_list
                yield vs
            else:
                for result in self.compute_cartesian(attr_list, start+1, length, id_list, value_list):
                    yield result

    def _package_size(self):
        self.product.update({
            "PackageLength": 20,
            "PackageWidth": 20,
            "PackageHeight": 10,
        })

    def deal_picture_zoom(self, pic_url):
        if self.url.startswith("https"):
            return "https:%s" % re.sub("_\d+x\d+\.\w+", "", pic_url)
        else:
            return "http:%s" % re.sub("_\d+x\d+\.\w+", "", pic_url)

    def export_product(self):
        self._package_size()
        self.product["Title"] = self._title()
        self.product["PictureURLs"] = self._pictures()
        self.product["ProductSpecifics"] = self._specifics()
        self.product["StartPrice"] = self._start_price()
        self.product["SourceInfo"] = self.source_info
        self.product["ProductSKUs"] = self._product_sku()
        self.product["ProductUnit"] = self._product_unit()
        self.product["Description"] = self._description()
        self.product["ListingDuration"] = "30"
        self.product["DispatchTimeMax"] = "7"
        self.product["GrossWeight"] = 0.5
        self.product["ParentSKU"] = self.gen_parent_sku() if self.product["ProductSKUs"] else ""
        return self.product
