# !/usr/bin/python
# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/8/5
# @description:

import traceback
from furion.lib.utils.logger_util import logger
from furion.views.api.ebay_api import EbayApiHandler


class EbayControl(object):

    ERRORS = {
        "AC_EBAY_0100": "标题长度超过80个字符",
        "AC_EBAY_0101": "标题为空",
        "AC_EBAY_0200": "商品详细描述为空",
        "AC_EBAY_0201": "商品详细描述超过500000个字符",
        "AC_EBAY_0300": "商品没有图片",
        "AC_EBAY_0301": "商品图片超过12张",
        "AC_EBAY_0400": "未设置商品有效期",
        "AC_EBAY_0401": "错误的商品有效期",
        "AC_EBAY_0500": "未设置商品备货时间",
        "AC_EBAY_0501": "错误的商品备货时间",
        "AC_EBAY_0600": "未设置商品状态",
        "AC_EBAY_0601": "错误的商品状态",
        "AC_EBAY_0700": "未设置商品起始价格",
        "AC_EBAY_0701": "未设置商品库存",
        "AC_EBAY_0800": "商品父SKU的长度超过50个字符",
        "AC_EBAY_0900": "商品未设置目录",
    }

    def __init__(self, shop, feed):
        self.feed = feed
        self.shop_id = shop.id
        self.errors = list()
        self.has_store = shop.session == "true"
        self.cate_uid = self._is_category_set()

    def _is_category_set(self):
        if not self.feed["CategoryUID"]:
            return 0
        return self.feed["CategoryUID"]

    def check_title(self):
        title = self.feed["Title"].strip()
        if not title:
            self.errors.append("AC_EBAY_0101")
        if len(title) > 80:
            self.errors.append("AC_EBAY_0100")

    def check_desc(self):
        desc = self.feed["Description"].strip()
        if not desc:
            self.errors.append("AC_EBAY_0200")
        if len(desc) > 500000:
            self.errors.append("AC_EBAY_0201")

    def check_pictures(self):
        pictures = self.feed["PictureURLs"]
        if not pictures:
            self.errors.append("AC_EBAY_0300")
        if len(pictures) > 12:
            self.errors.append("AC_EBAY_0301")

    def check_list_duration(self):
        if not self.cate_uid:
            return
        listing_duration = self.feed["ListingDuration"]
        if listing_duration == "":
            self.errors.append("AC_EBAY_0400")
            return
        listings = EbayApiHandler.get_listing_duration(self.cate_uid, self.has_store)
        for listing in listings["FixedPriceItem"]:
            if listing["value"] == str(listing_duration):
                return
        self.errors.append("AC_EBAY_0401")

    def check_condition(self):
        if not self.cate_uid:
            return
        condition_id = self.feed["Condition"]["ID"]
        conditions = EbayApiHandler.get_conditions(self.cate_uid)
        if len(conditions) == 0:
            return
        if not condition_id:
            self.errors.append("AC_EBAY_0600")
            return
        for condition in conditions:
            if condition["ID"] == condition_id:
                return
        self.errors.append("AC_EBAY_0601")

    def check_delivery_time(self):
        delivery_time = self.feed["DispatchTimeMax"]
        if not delivery_time:
            self.errors.append("AC_EBAY_0500")
            return
        if delivery_time not in ["0", "1", "2", "3", "4", "5", "10", "15", "20", "30", "40"]:
            self.errors.append("AC_EBAY_0501")
            return

    def check_start_price(self):
        sku_s = self.feed["ProductSKUs"]
        start_price = self.feed["StartPrice"]
        if len(sku_s) == 0 and not start_price:
            self.errors.append("AC_EBAY_0700")

    def check_stock(self):
        sku_s = self.feed["ProductSKUs"]
        quantity = self.feed["StartPrice"]
        if len(sku_s) == 0 and not quantity:
            self.errors.append("AC_EBAY_0701")

    def check_parent_sku(self):
        parent_sku = self.feed["ParentSKU"]
        if parent_sku and len(parent_sku) > 50:
            self.errors.append("AC_EBAY_0800")

    def check_category(self):
        if not self.cate_uid:
            self.errors.append("AC_EBAY_0900")

    def execute(self):
        try:
            self.check_title()
            self.check_start_price()
            self.check_category()
            self.check_condition()
            self.check_delivery_time()
            self.check_desc()
            self.check_list_duration()
            self.check_parent_sku()
            self.check_pictures()
            self.check_stock()
        except Exception, e:
            logger.error({
                "title": "商品验证失败",
                "shop_id": self.shop_id,
                "feed_id": str(self.feed["_id"]),
                "error": traceback.format_exc(e)
            })
        return self.errors