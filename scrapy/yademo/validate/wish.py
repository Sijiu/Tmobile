# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/12/22
# @description:

import re
import traceback
from furion.lib.utils.logger_util import logger


class WishControl(object):

    ERRORS = {
        "AC_WISH_0100": "标题长度超过255个字符",
        "AC_WISH_0101": "标题为空",
        "AC_WISH_0102": "商品标题存在非英文字符",
        "AC_WISH_0200": "商品详细描述为空",
        "AC_WISH_0201": "商品详细描述中包含HTML",
        "AC_WISH_0202": "商品详细描述中存在非英文字符",
        "AC_WISH_0400": "未设置商品运送时间",
        "AC_WISH_0401": "未设置商品运费",
        "AC_WISH_0402": "未设置商品SKU编码",
        "AC_WISH_0500": "未设置商品标签",
        "AC_WISH_0501": "商品标签超过10个",
        "AC_WISH_0502": "商品标签中包含非英文字符",
        "AC_WISH_0600": "未设置商品价格",
        "AC_WISH_0601": "商品价格小于0",
        "AC_WISH_0700": "商品没有图片",
        "AC_WISH_0800": "部分商品变体的库存超过1000件",
    }

    def __init__(self, shop, feed):
        self.feed = feed
        self.shop_id = shop.id
        self.errors = list()

    def check_title(self):
        title = self.feed["Title"].strip()
        if not title:
            return self.errors.append("AC_WISH_0100")
        if len(title) > 255:
            self.errors.append("AC_WISH_0101")
        if len(title) != len(title.encode("utf-8")):
            self.errors.append("AC_WISH_0102")
            
    def check_description(self):
        desc = self.feed["Description"].strip()
        if not desc:
            return self.errors.append("AC_WISH_0200")
        if re.compile("</?[a-zA-Z]+>").search(desc):
            self.errors.append("AC_WISH_0201")
        if len(desc) != len(desc.encode("utf-8")):
            self.errors.append("AC_WISH_0202")

    def check_shipping(self):
        ship_time = self.feed.get("ShippingTime").strip()
        if not ship_time:
            self.errors.append("AC_WISH_0400")
        ship_cost = self.feed.get("ShippingCost")
        if not ship_cost:
            self.errors.append("AC_WISH_0401")

    def check_quantity(self):
        for variation in self.feed["ProductSKUs"]:
            if int(variation["Stock"]) > 1000:
                return self.errors.append("AC_WISH_0800")

    def check_tags(self):
        tags = self.feed["KeyWords"]
        if "".join(tags).strip() == "":
            return self.errors.append("AC_WISH_0500")
        if len(tags) > 10:
            self.errors.append("AC_WISH_0501")
        for tag in tags:
            if len(tag) != len(tag.encode("utf-8")):
                return self.errors.append("AC_WISH_0502")

    def check_price(self):
        price = self.feed["StartPrice"]
        if not price:
            return self.errors.append("AC_WISH_0600")
        if float(price) <= 0:
            self.errors.append("AC_WISH_0601")

    def check_pictures(self):
        pictures = self.feed["PictureURLs"]
        if len(pictures) == 0:
            self.errors.append("AC_WISH_0700")

    def execute(self):
        try:
            self.check_title()
            self.check_description()
            self.check_shipping()
            self.check_tags()
            self.check_price()
            self.check_pictures()
        except Exception, e:
            logger.error({
                "title": "商品验证失败",
                "shop_id": self.shop_id,
                "feed_id": str(self.feed["_id"]),
                "error": traceback.format_exc(e)
            })
        return self.errors