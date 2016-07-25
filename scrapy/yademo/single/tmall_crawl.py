# !/usr/bin/python
# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/6/17
# @description:

import traceback
import re
from bs4 import BeautifulSoup
import requests
from furion.lib.handlers.template import generate_template
from furion.lib.utils.logger_util import logger
from furion.lib.utils.currency_util import transform


class TmallLink(object):

    def __init__(self, url):
        self.url = url
        self.item_id = self._extract_id()
        self.content = self._ready()
        self.soup = BeautifulSoup(self.content)
        self.product = generate_template()

    def _extract_id(self):
        temp = self.url.split("id=")[1]
        result = temp.split("&")[0]
        return result

    @property
    def source_info(self):
        return dict(
            SiteID="",
            Site="",
            Platform="Tmall",
            Link=self.url,
            ProductID=self.item_id
        )

    def _ready(self):
        try_times = 0
        while try_times < 5:
            try:
                try_times += 1
                res = requests.get(self.url)
                return res.text
            except Exception, e:
                logger.error(traceback.format_exc(e))
        raise Exception

    def _title(self):
        if self.soup.find("div", attrs={"class": "tb-detail-hd"}).find("h1").string:
            t = self.soup.find("div", attrs={"class": "tb-detail-hd"}).find("h1").string.strip()
            return t
        title = self.soup.find("div", attrs={"class", "tb-detail-hd"}).find("h1")
        return title.text.strip()

    def _description(self):
        zz_str = '{"api":{"descUrl":"([\s\S]+?)","fetchDcUrl"'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        desc_req = "http:" + result[0]
        res = requests.get(desc_req)
        res_text = res.text.strip()
        ss_str = "var desc='([\S\s]+?)';"
        pattern = re.compile(ss_str)
        result = pattern.findall(res_text)

        return result[0] if result else result

    def _start_price(self):
        headers = {
            "Accept": "*/*",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-GB,en-US;q=0.8,en;q=0.6",
            "Cache-Control": "max-age=0",
            "Connection": "keep-alive",
            "Cookie": "thw=cn; cna=pQvzDV5LlBACAdJMc4Ql5SM4; _cc_=WqG3DMC9EA%3D%3D; tg=0; x=e%3D1%26p%3D*%26s%3D0%26c%3D0%26f%3D0%26g%3D0%26t%3D0; ucn=center; uc3=nk2=&id2=&lg2=; tracknick=; ck1=; v=0; _tb_token_=s6zit0fJxPN7; mt=ci%3D-1_0; cookie2=1cb4f2bd14d437f3f3374a1d6a0337f9; t=baace121b692ea29de431e7f1135b94d; isg=99E24140071FDCAA23DBB17D1AC7D731; l=AggI5ZtfDlmqGHCvcqnR4Iu9WHgasWy7",
            "Host": "mdskip.taobao.com",
            "Referer": "http://detail.tmall.com/item.htm?spm=a220m.1000858.1000725.6.2nghk4&id=8095482851&areaId=110000&cat_id=50031543&rn=cae27e9c333e2834637f1bb048ad92ad&user_id=519286239&is_b=1&skuId=63004982478",
            "User-Agent": "Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/41.0.2272.118 Safari/537.36"
        }
        zz_str = 'url=\'([\s\S]+?)\''
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)
        url_ajax = "http:"+result[0]
        res_ajax = requests.get(url_ajax, headers=headers, timeout=30)
        cont_ajax = res_ajax.text
        zz_str_ajax = '\"priceInfo\"[\s\S]+?\"price\":\"([\s\S]+?)\"'
        pattern_ajax = re.compile(zz_str_ajax)
        res_ajax = pattern_ajax.findall(cont_ajax)
        price = res_ajax[0]
        return transform("CNY", "USD", float(price))

    def _brand(self):
        return self.soup.find(id="brand").string

    def _package_info(self):
        pass

    def _keywords(self):
        pass

    def _bullet_points(self):
        pass

    def _pictures(self):
        zz_str = '<ul id="J_UlThumb" class="tb-thumb tm-clear">([\s\S]+?)</ul>'
        pattern = re.compile(zz_str)
        result = pattern.findall(self.content)

        ss_str = '<a href="#"><img src="(.+?)" /></a>'
        pattern = re.compile(ss_str)
        result = pattern.findall(result[0])

        url_list = list()
        for img in result:
            img = "http:" + img.replace(".jpg_60x60q90", "")
            url_list.append(img)
        return url_list

    def _specifics(self):
        property_dom = self.soup.find("ul", attrs={"id": "J_AttrUL"})
        properties = list()
        property_str = property_dom.text
        for pro in property_str.strip().split("\n"):
            k, v = pro.split(":")
            properties.append({
                "Name": k.strip(),
                "Value": v.strip(),
                "NameID": "",
                "ValueID": ""
            })
        return properties

    def _product_unit(self):
        pass

    def _extract_value(self):
        pass

    def export_product(self):
        self.product["Title"] = self._title()
        self.product["Description"] = self._description()
        self.product["StartPrice"] = self._start_price()
        self.product["PictureURLs"] = self._pictures()
        self.product["ProductSpecifics"] = self._specifics()
        self.product["SourceInfo"] = self.source_info
        return self.product

