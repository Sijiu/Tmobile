# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/6/17
# @description:

import re
import json
import random
import requests
import traceback
import itertools
from string import uppercase
from bs4 import BeautifulSoup
from HTMLParser import HTMLParser
from furion.lib.handlers.template import generate_template
from furion.lib.nosql.redis_util import RedisUtil
from furion.lib.utils.logger_util import logger
from urllib import unquote


VARIATION_THEME = {
    "size_name": "Size",
    "color_name": "Color",
    "color_name-size_name": "Size-Color",
    "size_name-color_name": "Size-Color"
}


class AmazonLink(object):

    LABEL_TRANS = {
        "Style": "Color"
    }

    EXCEPT_LABELS = ["Product Packaging"]

    def __init__(self, url, site):
        logger.debug("amazon single crawl url: %s" % url)
        self._adapt_url(url)
        self.site = site
        self.proxies = RedisUtil("amazon_proxies", RedisUtil.RU_L)
        self.content = self._ready()
        self.soup = BeautifulSoup(self.content)
        self.item_id = self._extract_id()
        self.product = generate_template()

    def _adapt_url(self, url):
        if not url.startswith("http://"):
            self.url = "http://" + str(url)
        else:
            self.url = url

    def _extract_id(self):
        zz_str = r"/([\dA-Z]{10})[/?]*"
        pattern = re.compile(zz_str)
        result = pattern.findall(self.url)
        return result[0]

    @property
    def source_info(self):
        return dict(
            SiteID=self.site.id,
            Site=self.site.name,
            Platform="Amazon",
            Link=self.url,
            ProductID=self.item_id
        )

    def _ready(self):
        try_times = 0
        headers = {
            'Accept': '*/*',
            'Accept-Encoding': 'gzip, deflate',
            'Accept-Language': 'zh-CN,zh;q=0.8,en-US;q=0.5,en;q=0.3',
            'Connection': 'keep-alive',
            'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64; rv:37.0) Gecko/20100101 Firefox/37.0'
        }
        m = HTMLParser()
        proxy_times = 0
        while proxy_times < self.proxies.length:
            _proxy = self.proxies.next()
            if _proxy:
                proxy = {"http": _proxy}
            else:
                proxy = {}
            while try_times < 5:
                try_times += 1
                try:
                    error = "Sorry, we just need to make sure you're not a robot. " \
                            "For best results, please make sure your browser is accepting cookies."
                    res = requests.get(self.url, headers=headers, proxies=proxy, timeout=60)
                    if res.status_code != 200 or re.findall(error, res.text):
                        logger.warning("使用代理%s访问%s,出现被屏蔽问题!" % (str(_proxy), str(self.url)))
                        break
                        #raise Exception
                    return m.unescape(res.text)
                except Exception, e:
                    logger.info(traceback.format_exc(e))
            proxy_times += 1

    def _title(self):
        compile01 = "<span id=\"productTitle\" class=\"a-size-large\">([\s\S]+?)</span>"
        compile02 = "<title>([\s\S]+?)</title>"
        title01 = re.findall(compile01, self.content)
        title02 = re.findall(compile02, self.content)
        if title01:
            return title01[0]
        elif title02:
            return title02[0].replace("Amazon.com: ", "")
        else:
            return None

    def _description(self):
        zz_str = r"var iframeContent = \"(.+?)\"?;"
        pattern = re.compile(zz_str)
        s = pattern.findall(self.content)
        if s:
            return unquote(s[0].strip())
        else:
            pattern = r"<div id=\"productDescription\" class=\"a-section a-spacing-small\">([\s\S]+?)<style"
            if re.findall(pattern, self.content):
                des = re.findall(pattern, self.content)[0].strip()
                h_p = HTMLParser()
                return h_p.unescape(re.sub(r"\s{2,}", "", des))
            else:
                return ""

    def _start_price(self):
        if self.soup.find(id="priceblock_ourprice"):
            price = self.soup.find(id="priceblock_ourprice").string
            price = re.findall(r"(\d+.*\d*)", price)[0]
            return price.split("-")[0].strip().replace(",", "")
        elif re.findall(r"<span class='a-color-price'>.?([\d.]+?)</span>", self.content):
            price = re.findall(r"<span class='a-color-price'>.?([\d.]+?)</span>", self.content)[0]
            return price.split("-")[0].strip().replace(",", "")
        elif self.soup.find(id="priceblock_saleprice"):
            price = self.soup.find(id="priceblock_saleprice").string
            price = re.findall(r"(\d+.*\d*)", price)[0]
            return price.split("-")[0].strip().replace(",", "")
        else:
            return "0"

    def _brand(self):
        if self.soup.find(id="brand"):
            return self.soup.find(id="brand").string
        else:
            return ""

    def _package_info(self):
        w = re.findall(r"Shipping Weight:</b>\s+(.+?)</li>", self.content)
        shipping_weight = ""
        if w:
            shipping_weight = w[0].split(" ")[0]
            return {
                "ShippingWeight": shipping_weight
            }
        else:
            return {
                "ShippingWeight": shipping_weight
            }

    def _keywords(self):
        pass

    def _bullet_points(self):
        zz_str = r'<ul class="a-vertical a-spacing-none">([\s\S]+?)</ul>'
        pattern = re.compile(zz_str)
        m = pattern.findall(self.content)
        if m:
            point_content = r'<li.*><span class="a-list-item">(.+?)</span></li>'
            pattern = re.compile(point_content)
            result = pattern.findall(m[0].strip())
            h_p = HTMLParser()
            result = [h_p.unescape(bullet) for bullet in result]
            if len(result) < 5:
                for i in xrange(5-len(result)):
                    result.append("")
            return result
        else:
            return ["", "", "", "", ""]

    def _pictures(self):
        image_list = []
        images = re.findall(r"var data = ([\s\S]+?),\s+?'colorToAsin'", self.content)
        if images:
            image_list = re.findall(r"\"hiRes\":\"([\s\S]+?)\",\"thumb\"", images[0])
            if not image_list:
                image_list = re.findall(r"\"large\":\"([\s\S]+?)\",\"main\"", images[0])
        return image_list

    def _variation_specifics(self):
        variation = re.findall(r"P.register\('twister-js-init-mason-data', function\(\) \{\s+?var dataToReturn = ([\s\S]+?);\s+?return dataToReturn;", self.content)
        if  variation:
            result = re.sub(r'<[\s\S]+?>|</\S+?>', "", variation[0])
            variation_dict = json.loads(result.strip(";"))
            return variation_dict
        else:
            return {}

    def _variation_theme(self, dimensions):
        if len(dimensions) > 2:
            logger.info("变体属性个数大于2！")
            return ""
        theme = list()
        for item in dimensions:
            if item not in ["size_name", "color_name"]:
                logger.info("变体属性不支持")
                return ""
            else:
                theme.append(item)
        return "-".join(theme).strip("-")

    def variation_images(self):
        images = []
        images_str = 'data\["colorImages"\] = ([\s\S]+?);'
        result = re.compile(images_str).findall(self.content)
        if result:
            image_result = json.loads(result[0])
            for label in image_result:
                temp = []
                for ir in image_result[label]:
                    if "hiRes" in ir:
                        temp.append(ir["hiRes"])
                    else:
                        temp.append(ir["large"])
                images.extend(temp)
        return images

    def _product_variation(self, feed):
        variations = list()
        try:
            for k, v in feed["dimensionValuesDisplayData"].items():
                variation_specifics = []
                sku = {
                    "SKU": "",
                    "Price": self._start_price(),
                    "Stock": "",
                    "Asin": k,
                    "PictureURL": []
                }
                for i in xrange(len(v)):
                    spc = {
                        "Image": [],
                        "ValueID": "",
                        "NameID": "",
                        "Name": VARIATION_THEME[feed["dimensions"][i]],
                        "Value": v[i],
                    }
                    variation_specifics.append(spc)
                sku["VariationSpecifics"] = variation_specifics
                variations.append(sku)
            return variations
        except Exception as e:
            logger.info(traceback.format_exc(e))
            return []

    def _product_sku(self, start_price):
        value_str = '"variation_values":({.+?}),'
        result = re.compile(value_str).findall(self.content)
        if not result:
            return list()
        values = json.loads(result[0])
        label_str = '"variationDisplayLabels":({.+?}),'
        result = re.compile(label_str).findall(self.content)
        if not result:
            return list()
        label_dict = json.loads(result[0])
        name_value_dict = dict()
        for la_name, la_value in label_dict.iteritems():
            if la_value in self.EXCEPT_LABELS:
                continue
            new_label = self.LABEL_TRANS.get(la_value) or la_value
            name_value_dict[new_label] = values[la_name]
        images_str = 'data\["colorImages"\] = ([\s\S]+?);'
        result = re.compile(images_str).findall(self.content)
        images_dict = dict()
        if result:
            image_result = json.loads(result[0])
            for label in image_result:
                temp = []
                for ir in image_result[label]:
                    if "hiRes" in ir:
                        temp.append(ir["hiRes"])
                    else:
                        temp.append(ir["large"])
                images_dict[label] = temp
        combine_list = list()
        for name in name_value_dict:
            combine_list.append([
                "%s:%s" % (name, nv) for nv in name_value_dict[name]
            ])
        variations = list()
        sku_prefix = self.gen_sku_prefix() + "-"
        for vss in itertools.product(*combine_list):
            variations.append({
                "Stock": 999,
                "Price": start_price,
                "VariationSpecifics": [{
                    "NameID": "",
                    "Name": vs.split(":")[0],
                    "ValueID": "",
                    "Value": vs.split(":")[1],
                    "Image": images_dict.get(vs.split(":")[1]) or list()
                } for vs in vss],
                "SKU": sku_prefix + "-".join([vs.split(":")[1] for vs in vss]).replace(" ", "-"),
                "SkuID": "",
            })
        return variations

    @classmethod
    def gen_sku_prefix(cls):
        return "".join([random.choice(uppercase) for i in xrange(5)])

    def export_base(self):
        self.product["Title"] = self._title()
        self.product["Brand"] = self._brand()
        self.product["Description"] = self._description()
        self.product["BulletPoints"] = self._bullet_points()
        self.product["Manufacture"] = self.product["Brand"]
        self.product["StartPrice"] = self._start_price()
        self.product["SourceInfo"] = self.source_info
        self.product["PictureURLs"] = self._pictures()
        self.product.update(self._package_info())

    def export_product(self):
        self.export_base()
        self.product["ProductSKUs"] = self._product_sku(self.product["StartPrice"])
        return self.product

    def export_product_variation(self):
        self.export_base()
        feed = self._variation_specifics()
        if feed:
            self.product["CrawlImage"] = self.variation_images()
            variation_theme = self._variation_theme(feed["dimensions"])
            if variation_theme:
                self.product["VariationTheme"] = VARIATION_THEME[variation_theme]
                self.product["ProductSKUs"] = self._product_variation(self._variation_specifics())
        return self.product