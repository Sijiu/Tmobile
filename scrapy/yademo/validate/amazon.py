# !/usr/bin/python
# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/8/5
# @description:
import imghdr
import os

import re
import traceback
import cStringIO
import urllib2
from urlparse import urlparse
import requests
from furion.lib.model.category import Category
from furion.lib.model.session import sessionCM
from furion.lib.model.site import Site
from furion.lib.nosql.mongo_util import FeedsWarehouse
from furion.lib.utils.logger_util import logger


EUR_CLOTHING = ["653527", "650171", "688971"]

EUR = ["DE", "ES", "FR", "IN", "IT", "GB"]


class AmazonControl(object):

    ERRORS = {
        "AC_AMAZON_1000": "商品的Title不能为空",
        "AC_AMAZON_1001": "商品的Title长度不能超过500",
        "AC_AMAZON_2000": "商品的Brand长度超过50个字符",
        "AC_AMAZON_2001": "商品的Brand不能为空",
        "AC_AMAZON_3000": "商品的Manufacture不能为空",
        "AC_AMAZON_3001": "商品的Manufacture长度不能超过50个字符",
        "AC_AMAZON_4000": "商品的description长度超过2000个字符",
        "AC_AMAZON_4001": "商品的description不能为空",
        "AC_AMAZON_5000": "商品的关键字没有填完整，请补全",
        "AC_AMAZON_5001": "商品关键字的长度不能超过50",
        "AC_AMAZON_6000": "商品的BulletPoints没有填完整，请补全",
        "AC_AMAZON_6001": "商品的BulletPoint的长度不能超过500",
        "AC_AMAZON_7000": "商品的库存不能为空！",
        "AC_AMAZON_7001": "商品的库存只能是正整数！",
        "AC_AMAZON_8000": "当前类型下的产品必须参数没有填写完整",
        "AC_AMAZON_8001": "商品的MfrPartNumber长度不能超过40",
        "AC_AMAZON_8002": "商品的参数生厂商建议的最小年龄只能是数字",
        "AC_AMAZON_8003": "商品的参数生厂商建议的最大年龄只能是数字",
        "AC_AMAZON_8004": "商品的参数衣服材质成分的长度超过1000",
        "AC_AMAZON_8005": "RAM大小只能是数字，小数点前最多10位，小数点后最多2位",
        "AC_AMAZON_8006": "CPU速度只能是数字，小数点前最多10位，小数点后最多2位",
        "AC_AMAZON_8007": "ProcessorCount只能是正整数",
        "AC_AMAZON_8008": "硬盘容量只能是数字，小数点前最多10位，小数点后最多2位",
        "AC_AMAZON_9000": "商品的备货期数据不能为空",
        "AC_AMAZON_9001": "商品的备货期数据不合法必须是正整数且在1~30之间",
        "AC_AMAZON_1100": "商品的Mfr Part Number的长度超过40",
        "AC_AMAZON_1200": "商品的图片的url只接受.jpeg, .jpg, .gif格式",
        "AC_AMAZON_1201": "商品的图片的url无法访问！",
        "AC_AMAZON_1300": "商品的安全警告描述长度不能超过1500个字符",
        "AC_AMAZON_1400": "商品参数中的UnitCount只能是正整数！",
        "AC_AMAZON_1500": "商品参数Maximum Expandable Size(做大扩展尺寸)只能是数字，小数点前最多10位，小数点后最多2位",
        "AC_AMAZON_1501": "商品参数Line Size只能是数字，小数点前最多10位，小数点后最多2位",
        "AC_AMAZON_1502": "商品参数Paper Size只能是数字，小数点前最多10位，小数点后最多2位",
        "AC_AMAZON_1503": "变体属性Maximum Expandable Size(做大扩展尺寸)只能是数字，小数点前最多10位，小数点后最多2位",
        "AC_AMAZON_1504": "变体属性Line Size只能是数字，小数点前最多10位，小数点后最多2位",
        "AC_AMAZON_1505": "变体属性Paper Size只能是数字，小数点前最多10位，小数点后最多2位",
        "AC_AMAZON_1506": "商品参数中的NumberOfItems只能是正整数！",
        "AC_AMAZON_1507": "变体属性NumberOfItems只能是正整数！",
        "AC_AMAZON_1600": "商品的邮寄重量不能为空",
        "AC_AMAZON_1601": "商品的邮寄重量只能是数字，小数点前最多10位，小数点后最多2位",
        "AC_AMAZON_1700": "商品没有选择分类！",
        "AC_AMAZON_1800": "商品的sku长度不能超过40"
    }

    def __init__(self, shop, feed):
        self.feed = feed
        self.shop_id = shop.id
        self.errors = list()
        with sessionCM() as session:
            category = Category.find_by_id(session, str(feed["CategoryUID"]))
            self.site = Site.find_by_id(session, category.site_id)

    def execute(self):
        cate_id = self.feed["CategoryRoot"]
        if not cate_id:
            self.errors.append("AC_AMAZON_1700")
        self.errors = self.check_process(self.feed)
        return self.errors

    def check_process(self, feed):
        error_list = list()
        try:
            title_error = self.check_title(feed["Title"])
            des_error = self.check_description(feed["Description"])
            keywords_error = self.check_keywords(feed["KeyWords"])
            bullets_error = self.check_bullets(feed["BulletPoints"])
            max_time_error = self.check_max_time(feed["DispatchTimeMax"])
            specifics_error = self.check_specifics(feed["ProductSpecifics"])
            shipping_weight_error = self.check_weight(feed["ShippingWeight"])
            image_error = self.check_image(feed)
            sku_error = self.check_sku(feed)
            if title_error:
                error_list.append(title_error)
            if des_error:
                error_list.append(des_error)
            if keywords_error:
                error_list.append(keywords_error)
            if bullets_error:
                error_list.append(bullets_error)
            if specifics_error:
                error_list.extend(specifics_error)
            if max_time_error:
                error_list.append(max_time_error)
            if sku_error:
                error_list.append(sku_error)
            if image_error:
                error_list.append(image_error)
            if shipping_weight_error:
                error_list.append(shipping_weight_error)
            if feed["CategoryRoot"] == "707660" or "707347" and feed["VariationTheme"]:
                variation_errors = self.check_variation_specifics(feed["ProductSKUs"])
                error_list.extend(variation_errors)
        except Exception, e:
            logger.error({
                "title": "商品验证失败",
                "shop_id": self.shop_id,
                "feed_id": str(self.feed["_id"]),
                "error": traceback.format_exc(e)
            })
        return error_list

    @staticmethod
    def check_sku(feed):
        sku_list = []
        if feed["VariationTheme"]:
            for child in feed["ProductSKUs"]:
                sku_list.append(child["SKU"])
        else:
            sku_list = [feed["ParentSKU"]]
        for sku in sku_list:
            if len(sku) > 40:
                return "AC_AMAZON_1800"

    def check_variation_specifics(self, sku_specifics):
        error_list = list()
        for va_specifics in sku_specifics:
            for specifics in va_specifics["VariationSpecifics"]:
                print specifics
                if specifics["Name"] == "MaximumExpandableSize" and not self.num_format(specifics["Value"]):
                    error_list.append("AC_AMAZON_1503")
                elif specifics["Name"] == "LineSize"and not self.num_format(specifics["Value"]):
                    error_list.append("AC_AMAZON_1504")
                elif specifics["Name"] == "PaperSize"and not self.num_format(specifics["Value"]):
                     error_list.append("AC_AMAZON_1505")
                elif specifics["Name"] == "NumberOfItems" and not self.check_num_string(specifics["Value"]):
                    error_list.append("AC_AMAZON_1507")
        return error_list

    @staticmethod
    def check_image(feed):
        image_list = []
        if feed["VariationTheme"]:
            for child in feed["ProductSKUs"]:
                if isinstance(child["PictureURL"], list):
                    image_list.extend(child["PictureURL"])
                else:
                    image_list.append(child["PictureURL"])
        else:
            image_list = feed["PictureURLs"]
        for image in image_list:
            url_part = urlparse(image)
            image_format = os.path.splitext(url_part.path)[1].lower()
            if image_format not in [".jpg", ".jpeg", ".gif"]:
                return "AC_AMAZON_1200"

    @staticmethod
    def check_max_time(max_time):
        if not max_time:
            return "AC_AMAZON_9000"
        elif not max_time.isdigit() or int(max_time) > 30:
            return "AC_AMAZON_9001"

    @staticmethod
    def check_title(title):
        if not title:
            return "AC_AMAZON_1000"
        elif len(title) > 500:
            return "AC_AMAZON_1001"

    @staticmethod
    def check_description(desc):
        if not desc:
            return "AC_AMAZON_4001"
        elif len(desc) > 2000:
            return "AC_AMAZON_4000"

    @staticmethod
    def check_keywords(keywords):
        if not keywords or len(keywords) < 5:
            return "AC_AMAZON_5000"
        else:
            for key in keywords:
                if len(key) > 50:
                    return "AC_AMAZON_5001"
                elif not key:
                    return "AC_AMAZON_5000"

    def check_bullets(self, bullets):
        if not bullets:
            return "AC_AMAZON_6000"
        else:
            for bullet in bullets:
                if len(bullet) > 500:
                    return "AC_AMAZON_6001"

    def check_weight(self, shipping_weight):
        if not shipping_weight:
            return "AC_AMAZON_1600"
        elif not self.num_format(str(shipping_weight)):
            return "AC_AMAZON_1601"

    def check_specifics(self, specifics):
        error_list = list()
        for spec in specifics:
            if spec["Name"] == "MfrPartNumber" and spec["Value"] and len(spec["Value"]) > 40:
                error_list.append("AC_AMAZON_8001")
            elif spec["Name"] == "mfg_minimum" and spec["Value"] and self.check_num_string(str(spec["Value"])):
                error_list.append("AC_AMAZON_8002")
            elif spec["Name"] == "mfg_maximum" and spec["Value"] and self.check_num_string(str(spec["Value"])):
                error_list.append("AC_AMAZON_8003")
            elif spec["Name"] == "MaterialComposition" and spec["Value"] and len(spec["Value"]) > 1000:
                error_list.append("AC_AMAZON_8004")
            elif spec["Name"] == "RAMSize" and spec["Value"] and not self.num_format(spec["Value"]):
                error_list.append("AC_AMAZON_8005")
            elif spec["Name"] == "ProcessorSpeed" and spec["Value"] and not self.num_format(spec["Value"]):
                error_list.append("AC_AMAZON_8006")
            elif spec["Name"] == "ProcessorCount" and spec["Value"] and not self.check_num_string(spec["Value"]):
                error_list.append("AC_AMAZON_8007")
            elif spec["Name"] == "HardDriveSize" and spec["Value"] and not self.num_format(spec["Value"]):
                error_list.append("AC_AMAZON_8008")
            elif spec['Name'] == "ManufacturerSafetyWarning" and spec["Value"] and len(str(spec["Value"])) > 1500:
                error_list.append("AC_AMAZON_1300")
            elif spec['Name'] == "UnitCount" and spec["Value"] and not self.check_num_string(spec["Value"].split("+")[0].strip()):
                error_list.append("AC_AMAZON_1400")
            elif spec["Name"] == "MaximumExpandableSize" and spec["Value"] and not self.num_format(spec["Value"]):
                error_list.append("AC_AMAZON_1500")
            elif spec["Name"] == "LineSize" and spec["Value"] and not self.num_format(spec["Value"]):
                error_list.append("AC_AMAZON_1501")
            elif spec["Name"] == "PaperSize" and spec["Value"] and not self.num_format(spec["Value"]):
                 error_list.append("AC_AMAZON_1502")
            elif spec["Name"] == "NumberOfItems" and spec["Value"] and not self.check_num_string(spec["Value"]):
                error_list.append("AC_AMAZON_1506")
        return error_list

    @staticmethod
    def check_num_string(num_string):
        try:
            if int(num_string):
                return True
        except ValueError:
            return False

    @staticmethod
    def num_format(num_string):
        if re.match(r"[+-]?\d{,10}.?\d{,2}$", str(num_string)):
            return True
        else:
            return False

    @staticmethod
    def get_picture(picture_url):
        try_times = 0
        while try_times <= 5:
            try:
                res = requests.get(picture_url, timeout=60)
                return res
            except Exception, e:
                logger.error(traceback.format_exc(e))
                try_times += 1
        return None


