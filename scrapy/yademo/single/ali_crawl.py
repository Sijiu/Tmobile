# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/10/16
# @description:


import HTMLParser
import json
import re
from string import uppercase
import traceback
import urllib
import requests
from furion.lib.utils.furion_exception import TimeoutException
from furion.lib.handlers.template import generate_template
from furion.lib.utils.ali_unit import find_by_zh_name
from furion.lib.utils.base import random
from furion.lib.utils.currency_util import transform
from furion.lib.utils.logger_util import logger


class AliLink(object):

    def __init__(self, url, site=None):
        self.url = url
        self.site = site
        self.content = self._ready()
        self.item_id = self._extract_id()
        self.product = generate_template()
        self.specifics = dict()
        self.parser = HTMLParser.HTMLParser()

    def _extract_id(self):
        zz_str = r"offer/(\d+)\.html"
        pattern = re.compile(zz_str)
        result = pattern.findall(self.url)
        return result[0]

    @property
    def source_info(self):
        return {
            "SiteID": "",
            "Site": "",
            "Platform": "1688",
            "ProductID": self.item_id,
            "Link": self.url
        }

    def _ready(self):
        try_times = 0
        headers = {
            "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
            "Connection": "keep-alive",
            "Cookie": 'ali_beacon_id=119.255.38.142.1446547899495.954328.5; cna=kX+/DiwN6DkCAXf/Jo5ReeN7; h_keys="%u8fde%u8863%u88d9#%u4fdd%u6e29%u676f#%u8fd0%u52a8%u88e4"; ali_apache_track="c_ms=1|c_mid=b2b-579281383|c_lid=xuhe789"; _cn_slid_=efTuaxRtdL; ad_prefer="2015/11/24 14:57:30"; __last_loginid__=xuhe789; last_mid=b2b-579281383; ali_ab=119.255.38.142.1446547900523.6; JSESSIONID=8L78FIqv1-umbUlQFxDUq4KRXiiA-9lf77VP-5DMN; _csrf_token=1448511270570; alicnweb=touch_tb_at%3D1448511354133%7Clastlogonid%3Dxuhe789; sec=565687a0a3893c2c7e1a16162431ad6c962f0978; CNZZDATA1253659577=1397154625-1446546533-http%253A%252F%252Fs.1688.com%252F%7C1448506232; __cn_logon__=false; _tmp_ck_0="XVl%2BVgQl5eVO4ZpG%2BwZGcaBXm7p3H2NVWc3BgnPfLW7sLMASnjeOmQltFKtEX%2F%2F0N9Eq4RAhkJ6JdfX4Odzajy2wIu6%2FQX8%2F7I6jTFSkKiQClrogQqQGnD89BsHmvUFtUrQ5nMYwaCMqwdKzP8%2FRuuquBPv4GbBND6XdlCE4vDhZtG3GUN1rrjb9nRmUFozrPmWg7roOZZAsXbdRYSdsu%2BkqXyI0%2F8VJ1FoMdmhwfu7tONVCkk4LuHvZb%2Bd8CQnz%2F4pNsr2bNNQChjZJ%2Fvw0H%2FrQokoWHhBS0dGWj1lWee%2BFtCLcDaF6iOXhJ%2F235GZteDq0arC%2FASHMXh15%2Fd4Ct2wfCmJORYvkICaZsULnq4RIcY6Byp6q702GlWko095Spfz38aR9bOM%3D"; isg=4D5A27DFE98A3907243CCFB23139B0E3; l=Aioqhpa-ItUXndKJ5FPQO7B2-p7MoK5j',
            "Host": "detail.1688.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36",
            "X-Requested-With": "XMLHttpRequest"
        }
        while try_times < 5:
            try:
                res = requests.get(self.url, timeout=10)
                return res.text
            except Exception, e:
                logger.info(traceback.format_exc(e))
                try_times += 1
        raise TimeoutException

    def _title(self):
        title_str = '<title>.+?[_\-](.+?)[_\-\.].+?</title>'
        title_pattern = re.compile(title_str)
        title_obj = title_pattern.findall(self.content)
        if title_obj:
            title = title_obj[0].strip()
            return self.parser.unescape(title)
        else:
            return ""

    def _description(self):
        desc_str = 'data-tfs-url="(.+?)"'
        desc_pattern = re.compile(desc_str)
        desc_obj = desc_pattern.findall(self.content)
        desc_req = desc_obj[0].strip()
        res = requests.get(desc_req)
        print desc_req
        res_text = res.text
        if "dsc.taobaocdn.com" in desc_req:
            ss_str = "var desc='(.+?)';"
            pattern = re.compile(ss_str)
            result = pattern.findall(res_text)
            return result[0]
        elif re.compile("img\d*.taobaocdn.com").search(desc_req):
            print "!!!!!!"
            print res_text
            ss_str = 'var offer_details=({"content":".+?"});'
            pattern = re.compile(ss_str)
            result = pattern.findall(res_text)
            desc_dict = json.loads(result[0])
            return self.parser.unescape(desc_dict["content"])
        else:
            raise Exception

    def _specifics(self):
        spec_str = 'de-feature">(.+?)</td>\s*<td class="de-value">(.+?)<'
        spec_pattern = re.compile(spec_str)
        spec_obj = spec_pattern.findall(self.content)
        result = {"ProductSpecifics": list()}
        for spec in spec_obj:
            spec = spec[0].replace("<br/>", "").strip(), spec[1].replace("<br/>", "").strip()
            if spec[0] == u"建议零售价" or spec[0] == u"货源类别":
                continue
            result["ProductSpecifics"].append({
                "Name": spec[0],
                "Value": spec[1],
                "NameID": "",
                "ValueID": ""
            })
        return result

    def _package_size(self):
        self.product.update({
            "PackageLength": 20,
            "PackageWidth": 20,
            "PackageHeight": 10,
        })

    @classmethod
    def deal_picture_zoom(cls, pic_url):
        return re.sub("\.\d+x\d+", "", pic_url)

    def _pictures(self):
        pictures = list()
        pic_str = 'a class="box-img" href[\s\S]+?<img src="(.+?)"'
        pic_pattern = re.compile(pic_str)
        pic_obj = pic_pattern.findall(self.content)
        for pic in pic_obj:
            if pic in pictures:
                continue
            pictures.append(self.deal_picture_zoom(pic))
        return pictures

    def _product_sku(self, start_price):
        pu_str = "var iDetailData = ({[\s\S]+?});"
        pu_pattern = re.compile(pu_str)
        pu_obj = pu_pattern.findall(self.content)
        if not pu_obj:
            return {"ProductSKUs": list()}
        sku_info_str = self.parser.unescape(pu_obj[0]).strip()
        sku_info = json.loads(sku_info_str)
        if not sku_info:
            return list()
        sku_info = sku_info["sku"]
        sku_prop_dict = dict()
        for sku_prop in sku_info["skuProps"]:
            for value in sku_prop["value"]:
                image_url = value.get("imageUrl")
                sku_prop_dict[value["name"]] = {
                    "image": [image_url] if image_url else list(),
                    "sku_name": sku_prop["prop"],
                }
        variations = list()
        for sku_combine, sku_item in sku_info["skuMap"].iteritems():
            variation, vs = dict(), list()
            for vs_value in sku_combine.split(">"):
                vs.append({
                    "Image": sku_prop_dict[vs_value]["image"],
                    "Name": sku_prop_dict[vs_value]["sku_name"],
                    "Value": vs_value,
                    "NameID": "",
                    "ValueID": ""
                })
            variation["VariationSpecifics"] = vs
            variation["Price"] = transform("CNY", "USD", start_price) if start_price else ""
            variation["Stock"] = sku_item["canBookCount"]
            variation["SkuID"] = ""
            variation["SKU"] = ""
            variations.append(variation)
        return {"ProductSKUs": variations}

    def _other_info(self):
        req_header = "http://laputa.1688.com/offer/ajax/widgetList.do"
        params = {
            "callback": "jQuery17203066696197321128_1445515045",
            "blocks": "",
            "data": "offerdetail_ditto_postage",
            "offerId": self.item_id
        }
        url = "?".join([req_header, urllib.urlencode(params)])
        response = requests.get(url)
        result = dict()
        if not self.product["StartPrice"]:
            st_str = 'price": *"([\.\d]+)",'
            st_pattern = re.compile(st_str)
            st_obj = st_pattern.findall(response.text)
            price = st_obj[0].strip()
            if isinstance(price, basestring):
                price = price.replace(",", "")
            result["StartPrice"] = transform("CNY", "USD", float(price))
        pack_str = 'unitWeight":([\s\S]+?)}'
        pack_pattern = re.compile(pack_str)
        pack_obj = pack_pattern.findall(response.text)
        if pack_obj:
            pck = pack_obj[0].strip()
            gross_weight = float(pck) or 0.5
            result["GrossWeight"] = str(gross_weight)
        unit_str = "'unit': *'(.+?)'"
        unit_pattern = re.compile(unit_str)
        unit_obj = unit_pattern.findall(self.content)
        zh_name = unit_obj[0] if unit_obj else ""
        result["ProductUnit"] = find_by_zh_name(zh_name)["code"]
        return result

    @classmethod
    def gen_sku_prefix(cls):
        return "".join([random.choice(uppercase) for i in xrange(5)])

    def export_product(self):
        self._package_size()
        self.product["Title"] = self._title()
        self.product["Description"] = self._description()
        self.product["PictureURLs"] = self._pictures()
        self.product["SourceInfo"] = self.source_info
        self.product["ListingDuration"] = "30"
        self.product["DispatchTimeMax"] = "7"
        self.product.update(self._other_info())
        self.product.update(self._specifics())
        self.product.update(self._product_sku(self.product["StartPrice"]))
        return self.product