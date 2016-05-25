# !/usr/bin/python
# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/8/5
# @description:

import re
import traceback
from furion.lib.utils.logger_util import logger
from furion.views.api.ali_api import AliApiHandler


class AliControl(object):

    ERRORS = {
        "AC_ALI_0100": "商品标题为空",
        "AC_ALI_0101": "商品标题超过128字符",
        "AC_ALI_0102": "商品标题存在中文字符",
        "AC_ALI_0103": "商品标题存在非法字符",
        "AC_ALI_0200": "商品详细描述为空",
        "AC_ALI_0201": "商品详细描述中存在中文字符",
        "AC_ALI_0202": "商品详细描述超过60000个字符",
        "AC_ALI_0203": "商品详细描述中存在大量非法字符",
        "AC_ALI_0300": "商品发货期为空",
        "AC_ALI_0301": "商品发货期不正确",
        "AC_ALI_0400": "商品类目为空",
        "AC_ALI_0600": "未填写商品价格",
        "AC_ALI_0601": "商品价格不在0-100000范围内",
        "AC_ALI_0700": "商品没有图片",
        "AC_ALI_0800": "商品未设置包装信息",
        "AC_ALI_0801": "商品包装信息不是数字",
        "AC_ALI_0802": "商品包装长度不在1-700之内",
        "AC_ALI_0803": "商品包装宽度不在1-700之内",
        "AC_ALI_0804": "商品包装高度不在1-700之内",
        "AC_ALI_0900": "商品毛重未设置",
        "AC_ALI_0901": "商品毛重不在0.001-500.000之内",
        "AC_ALI_1000": "商品有效天数未设置",
        "AC_ALI_1001": "商品有效天数不在1-30之内",
        "AC_ALI_1101": "商品计量单位未设置",
        "AC_ALI_1200": "商品未设置目录",
        "AC_ALI_1300": "必要的商品参数未填写",
    }
    BATCH_ALLOWED = [
        "AC_ALI_0300", "AC_ALI_0301", "AC_ALI_0500", "AC_ALI_0501",
        "AC_ALI_0502", "AC_ALI_0503", "AC_ALI_0800", "AC_ALI_0801",
        "AC_ALI_0802", "AC_ALI_0803", "AC_ALI_0804", "AC_ALI_0805",
        "AC_ALI_0900", "AC_ALI_0901", "AC_ALI_1000", "AC_ALI_1001",
    ]

    def __init__(self, shop, feed):
        self.feed = feed
        self.shop_id = shop.id
        self.errors = list()
        self.cate_uid = self._is_category_set()

    def _is_category_set(self):
        if not self.feed["CategoryUID"]:
            return 0
        return self.feed["CategoryUID"]

    def check_title(self):
        title = self.feed["Title"]
        title = title.strip()
        if not title:
            self.errors.append("AC_ALI_0100")
        if len(title) > 128:
            self.errors.append("AC_ALI_0101")
        pattern = re.compile(u'[\u4e00-\u9fa5]+')
        if pattern.search(title):
            self.errors.append("AC_ALI_0102")
        if len(title) != len(title.encode("utf-8")):
            self.errors.append("AC_ALI_0103")

    def check_description(self):
        desc = self.feed["Description"].strip()
        if not desc:
            self.errors.append("AC_ALI_0200")
        # pattern = re.compile(u'[\u4e00-\u9fa5]+')
        # if pattern.search(desc):
        #     self.errors.append("AC_ALI_0201")
        if len(desc) > 60000:
            self.errors.append("AC_ALI_0202")
        # if len(desc.encode("utf-8")) - len(desc) > 100:
        #     self.errors.append("AC_ALI_0203")

    def check_delivery_time(self):
        delivery_time = self.feed["DispatchTimeMax"]
        if not delivery_time:
            self.errors.append("AC_ALI_0300")
            return
        delivery_limit = AliApiHandler.get_delivery_time(self.feed["CategoryUID"])
        if int(delivery_time) > delivery_limit:
            self.errors.append("AC_ALI_0301")

    def check_category(self):
        category_id = self.feed["Category"]["ID"]
        if not category_id:
            self.errors.append("AC_ALI_0400")

    def check_specifics(self):
        specifics = self.feed["ProductSpecifics"]
        if not self.cate_uid:
            self.errors.append("AC_ALI_1200")
            return
        pros = AliApiHandler.get_required_pros(self.cate_uid)

        def check_pro_cell(pro):
            for specific in specifics:
                if specific["NameID"] == "":
                    continue
                if int(specific["NameID"]) == pro["name_id"]:
                    if specific["ValueID"]:
                        return True
                    elif pro["show_type"] == "input" and specific["Value"]:
                        return True
            return False
        exc = set()
        for p in pros:
            if not check_pro_cell(p):
                exc.add("AC_ALI_1300")
        self.errors.extend(list(exc))

    def check_start_price(self):
        price = self.feed["StartPrice"]
        if not self.feed.get("ProductSKUs") and not price:
            self.errors.append("AC_ALI_0600")
        if price and not (0 < float(price) < 100000):
            self.errors.append("AC_ALI_0601")

    def check_pictures(self):
        pictures = self.feed["PictureURLs"]
        if len(pictures) == 0:
            self.errors.append("AC_ALI_0700")

    def check_package(self):
        pl = self.feed["PackageLength"]
        pw = self.feed["PackageWidth"]
        ph = self.feed["PackageHeight"]
        if pl and pw and ph:
            try:
                pl, pw, ph = int(pl), int(pw), int(ph)
            except ValueError:
                self.errors.append("AC_ALI_0801")
                return
            if not (0 < int(pl) < 701):
                self.errors.append("AC_ALI_0802")
            if not (0 < int(pw) < 701):
                self.errors.append("AC_ALI_0803")
            if not (0 < int(ph) < 701):
                self.errors.append("AC_ALI_0804")
        else:
            self.errors.append("AC_ALI_0800")

    def check_gross_weight(self):
        gross_weight = self.feed["GrossWeight"]
        if not gross_weight:
            self.errors.append("AC_ALI_0900")
            return
        if not (0.001 < float(gross_weight) < 500.000):
            self.errors.append("AC_ALI_0901")
            return

    def check_listing_duration(self):
        listing_duration = self.feed["ListingDuration"]
        print repr(listing_duration)
        if not listing_duration:
            self.errors.append("AC_ALI_1000")
            return
        if not (0 < int(listing_duration) < 31):
            self.errors.append("AC_ALI_1001")
            return

    def check_product_unit(self):
        unit = self.feed["ProductUnit"]
        if not unit:
            self.errors.append("AC_ALI_1101")

    def execute(self):
        try:
            self.check_title()
            self.check_category()
            self.check_delivery_time()
            self.check_description()
            self.check_gross_weight()
            self.check_listing_duration()
            self.check_package()
            self.check_pictures()
            self.check_product_unit()
            self.check_start_price()
            self.check_specifics()
        except Exception, e:
            logger.error({
                "title": "商品验证失败",
                "shop_id": self.shop_id,
                "feed_id": str(self.feed["_id"]),
                "error": traceback.format_exc(e)
            })
        return self.errors