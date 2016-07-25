# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/6/17
# @description:

import re
import time
import random
import requests
import traceback
import HTMLParser
import ujson as json
from string import uppercase
from urllib import urlencode
from furion.lib.handlers.feed_template import FeedTemplate
from furion.lib.handlers.template import generate_template
from furion.lib.model.category import Category
from furion.lib.model.session import sessionCM
from furion.lib.nosql.mongo_util import FeedsWarehouse
from furion.lib.utils.logger_util import logger
from furion.lib.utils.ali_unit import find_by_en_name
from furion.lib.utils.furion_exception import TimeoutException


class SmtLink(object):

    def __init__(self, url, site):
        self.site = site
        self.url = self._adapt_url(url)
        self.item_id = self._extract_id()
        self.content = self._ready()
        self.product = generate_template()
        self.spec_entry = FeedsWarehouse("ali_specifics")
        self.specifics = dict()
        self.parser = HTMLParser.HTMLParser()

    def _adapt_url(self, url):
        return re.sub("://[a-z]+\.aliexpress\.com", "://www.aliexpress.com", url)

    def _extract_id(self):
        zz_str = r"[/_](\d+)\.html"
        pattern = re.compile(zz_str)
        result = pattern.findall(self.url)
        return result[0]

    @property
    def source_info(self):
        return dict(
            SiteID=self.site.id,
            Site=self.site.name,
            Platform="AliExpress",
            Link=self.url,
            ProductID=self.item_id
        )

    def _ready(self):
        try_times = 0
        headers = {
            "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
            "Connection": "keep-alive",
            "Host": "www.aliexpress.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36",
        }
        while try_times < 5:
            try:
                res = requests.get(self.url, headers=headers, timeout=60)
                return res.text
            except Exception, e:
                logger.info(traceback.format_exc(e))
                try_times += 1
        raise TimeoutException

    def _title(self):
        title_str = '<h1 class="product-name" itemprop="name">(.+?)</h1>'
        title_pattern = re.compile(title_str)
        title_obj = title_pattern.findall(self.content)
        title = title_obj[0].strip()
        if title_obj:
            return self.parser.unescape(title)
        else:
            return ""

    def _description(self):
        product_id = self.source_info["ProductID"]
        headers = {
            "Accept": "text/javascript, application/javascript, application/ecmascript, application/x-ecmascript, */*; q=0.01",
            "Accept-Encoding": "gzip, deflate, sdch",
            "Accept-Language": "en-US,en;q=0.8,zh-CN;q=0.6,zh;q=0.4",
            "Connection": "keep-alive",
            "Host": "www.aliexpress.com",
            "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/43.0.2357.124 Safari/537.36",
        }
        timestamp = int(time.time()*1000)
        res = requests.get(
            "http://www.aliexpress.com/getDescModuleAjax.htm?productId=%s&t=%d" % (product_id, timestamp),
            headers=headers
        )
        res_text = res.text
        logger.info(res_text)
        desc = res_text.strip().replace("window.productDescription='", "")[: -2]
        return self.get_size_model() + desc

    def _start_price(self):
        price_str = 'minPrice="([\d\.]+)";'
        price_pattern = re.compile(price_str)
        price_obj = price_pattern.findall(self.content)
        if not price_obj:
            return ""
        else:
            return price_obj[0]

    def _product_unit(self):
        unit_str = 'Unit Type:</dt>\s*<dd>(.+)</dd>'
        unit_pattern = re.compile(unit_str)
        unit_obj = unit_pattern.findall(self.content)
        if not unit_obj:
            return {"ProductUnit": u"100000015"}
        info = unit_obj[0]
        if info.startswith("lot"):
            lot_str = "lot \((\d+) (\w+)/lot\)"
            lot_pattern = re.compile(lot_str)
            lot_obj = lot_pattern.findall(info)
            if not lot_obj:
                return {"ProductUnit": u"100000015"}
            unit = find_by_en_name(lot_obj[0][1])
            return {
                "PackageType": True,
                "LotNum": lot_obj[0][0],
                "ProductUnit": unit["code"]
            }
        unit = find_by_en_name(info)
        return {"ProductUnit": unit["code"]}

    def _package_size(self):
        pack_str = '<dd class="pnl-packaging-size" rel="([\d|]+)">'
        pack_pattern = re.compile(pack_str)
        pack_obj = pack_pattern.findall(self.content)
        pack = {
            "PackageLength": "",
            "PackageWidth": "",
            "PackageHeight": "",
        }
        if pack_obj:
            l, w, h = pack_obj[0].split("|")
            pack["PackageLength"], pack["PackageWidth"], pack["PackageHeight"] = int(l), int(w), int(h)
            return pack
        else:
            return pack

    def _gross_weight(self):
        pack_str = 'pnl-packaging-weight" rel="([\d\.]+)">'
        pack_pattern = re.compile(pack_str)
        pack_obj = pack_pattern.findall(self.content)
        if pack_obj:
            return re.sub("\.+", ".", pack_obj[0])
        else:
            return ""

    def _pictures(self):
        pictures = list()
        gallery_str = '<img.+?src="(.+?)" data-role="thumb"'
        gallery_pattern = re.compile(gallery_str)
        gallery_obj = gallery_pattern.findall(self.content)
        if gallery_obj:
            pictures.append(self.deal_picture_zoom(gallery_obj[0]))
        image_str = 'image-nav-item" ><span><img.+?src="(.+)"/>'
        image_pattern = re.compile(image_str)
        image_obj = image_pattern.findall(self.content)
        for image in image_obj:
            image = self.deal_picture_zoom(image)
            if image in pictures:
                continue
            pictures.append(image)
        return pictures

    @classmethod
    def deal_picture_zoom(cls, pic_url):
        return re.sub("\.(jpg|jpeg)_\d+x\d+", "", pic_url)

    def _specifics(self):
        spec_str = 'class="ui-attr-list util-clearfix">\s*<dt.*?>(.+?):</dt>\s*<dd title="(.+?)">'
        spec_pattern = re.compile(spec_str)
        spec_obj = spec_pattern.findall(self.content)
        if not spec_obj:
            return list()
        specifics = list()
        no_nid_counter = 0
        for name, multi_value in spec_obj:
            if self.check_spec_unique(name, specifics):
                continue
            name, multi_value = self.parser.unescape(name.strip()), self.parser.unescape(multi_value.strip())
            if multi_value.lower() == "none" or not multi_value:
                continue
            name_id = self._extract_name_id(name)
            if name_id:
                name_type = self._extract_name_type(name)
                if name_type == "check_box":
                    multi_value = multi_value.split(",")
                else:
                    multi_value = [multi_value]
                for value in multi_value:
                    value_id = self._extract_value_id(name, value)
                    if name_type != "input" and not value_id:
                        continue
                    specifics.append({
                        "NameID": name_id,
                        "Name": name,
                        "ValueID": value_id,
                        "Value": value.strip()
                    })
                continue
            if no_nid_counter < 10:
                specifics.append({
                    "NameID": "",
                    "Name": name,
                    "ValueID": "",
                    "Value": multi_value.strip()
                })
                no_nid_counter += 1
        return specifics

    @classmethod
    def check_spec_unique(cls, name, specifics):
        repeat = False
        for spec in specifics:
            if spec["Name"] == name:
                repeat = True
        return repeat

    def _category(self):
        cate_str = 'window\.runParams\.categoryId="(\d+)";'
        cate_pattern = re.compile(cate_str)
        cate_obj = cate_pattern.findall(self.content)
        if cate_obj:
            return cate_obj[0]
        else:
            return ""

    def _product_sku(self):
        structure = dict()
        prefix = self.gen_sku_prefix()
        sku_products_str = "var skuProducts=(\[[\s\S]+?\]);"
        sku_products_pattern = re.compile(sku_products_str)
        sku_products_obj = sku_products_pattern.findall(self.content)
        if sku_products_obj:
            spo = sku_products_obj[0]
            product_sku = json.loads(spo)
            if re.compile("skuPrice\":\"([\d\.]+)").search(spo):
                self.clear_quote(product_sku)
        else:
            return list()

        pro_multi_sku = list()
        bulk_price = product_sku[0]["skuVal"].get("skuBulkPrice")
        if bulk_price:
            sku_price = product_sku[0]["skuVal"].get("skuPrice")
            discount = self.compute_discount(sku_price, bulk_price)
            structure["BulkSell"] = {
                "BulkOrder": product_sku[0]["skuVal"]["bulkOrder"],
                "BulkDiscount": discount
            }
        else:
            structure["BulkSell"] = False
        if not product_sku[0].get("skuAttr"):
            structure["Quantity"] = product_sku[0]["skuVal"]["inventory"]
            structure["StartPrice"] = product_sku[0]["skuVal"]["skuPrice"]
            return structure
        if not self.specifics:
            return list()
        quantity = 0
        for ps in product_sku:
            pro_vs = list()
            index = 1
            sku_labels = [prefix]
            for nv_comp in ps["skuAttr"].split(";"):
                nid, vid = nv_comp.split(":")
                if nid == "200007763":
                    continue
                vv = ""
                if "#" in vid:
                    vid, vv = vid.split("#")
                nid, vid = int(nid), int(vid)
                value = self._extract_value(nid, vid)
                image = self._find_sku_image(index, vid)
                pro_vs.append({
                    "Name": self._extract_name(nid),
                    "NameID": nid,
                    "Value": (vv or value).strip(),
                    "ValueID": vid,
                    "Image": [image] if image else list()
                })
                index += 1
                sku_labels.append(value)
            if pro_vs:
                pro_multi_sku.append({
                    "Stock": ps["skuVal"]["inventory"],
                    "Price": ps["skuVal"]["skuPrice"],
                    "VariationSpecifics": pro_vs,
                    "SKU": "-".join(sku_labels).replace(" ", "-")[0: 20],
                    "SkuID": ps["skuAttr"]
                })
            quantity += ps["skuVal"]["inventory"]
        structure["Quantity"] = quantity
        structure["ProductSKUs"] = pro_multi_sku
        return structure

    def _extract_name(self, nid):
        for spec in self.specifics["attributes"]:
            if spec["id"] == nid:
                return spec["names"]["en"]
        raise Exception

    def _extract_value(self, nid, vid):
        for spec in self.specifics["attributes"]:
            if spec["id"] != nid:
                continue
            for spec_value in spec["values"]:
                if spec_value["id"] == vid:
                    return spec_value["names"]["en"]
        raise Exception

    def _extract_name_id(self, name):
        for spec in self.specifics["attributes"]:
            if spec["sku"]:
                continue
            if spec["names"]["en"] == name:
                return spec["id"]
        return ""

    def _extract_name_type(self, name):
        for spec in self.specifics["attributes"]:
            if spec["names"]["en"] == name:
                return spec["attributeShowTypeValue"]
        return ""

    def _extract_value_id(self, name, value):
        other_option = False
        for spec in self.specifics["attributes"]:
            if spec["sku"]:
                continue
            if spec["names"]["en"] != name:
                continue
            other_option = 4 in [sv["id"] for sv in spec.get("values", list())]
            for spec_value in spec.get("values", list()):
                if spec_value["names"]["en"] == value:
                    return spec_value["id"]
        return 4 if other_option else ""

    def _find_sku_image(self, index, vid):
        sku_id = "sku-%d-%d" % (index, vid)
        image_str = '<a.+?id="%s".+?><img.+?src="(http://.+?)"' % sku_id
        image_pattern = re.compile(image_str)
        image_obj = image_pattern.findall(self.content)
        if image_obj:
            return self.deal_picture_zoom(image_obj[0])
        else:
            return ""

    @classmethod
    def gen_sku_prefix(cls):
        return "".join([random.choice(uppercase) for i in xrange(5)])

    @classmethod
    def gen_parent_sku(cls):
        return "".join([random.choice(uppercase) for i in xrange(10)])

    def get_size_model(self):
        size_id_g = re.compile('pageSizeID="(\w+)";').search(self.content)
        if not size_id_g:
            return ""
        size_ty_g = re.compile('pageSizeType="(\w+)";').search(self.content)
        if not size_ty_g:
            return ""
        size_ad_g = re.compile('adminSeq="(\w+)";').search(self.content)
        if not size_ad_g:
            return ""
        size_id = size_id_g.groups()[0]
        size_ty = size_ty_g.groups()[0]
        size_ad = size_ad_g.groups()[0]
        params = {
            "pageSizeID": size_id,
            "sellerId": size_ad,
            "pageSizeType": size_ty
        }
        req_head = "http://www.aliexpress.com/productSizeAjax.htm"
        req_url = "?".join([req_head, urlencode(params)])
        headers = {
            "Referer": self.url
        }
        res = requests.get(req_url, headers=headers)
        size_model = res.json()
        if not size_model.get("isSuccess"):
            return ""
        html = self.complete_size_html(size_model)
        return html

    @classmethod
    def complete_size_html(cls, size_model):
        tb_style = "width:100%;border:1px solid #e0e0e0;border-collapse:collapse;text-align:center"
        im_style = "display:block;margin:0 auto"
        th_style = "padding:6px 0;border:1px solid #e0e0e0;height: 40px;font-size: 16px;color: #333; background-color: #e0e0e0"
        td_style = "padding:6px 0;border:1px solid #e0e0e0;height: 30px;font-size: 16px;color: #333;"
        table_html = "<table style=\"%s\" cellpadding=\"2\" cellspacing=\"0\" border=\"1\" bordercolor=\"#e0e0e0\"><thead>%s</thead><tbody>%s</tbody></table>"
        table_head = ""
        for title in size_model["sizeAttr"]["title"]:
            table_head += "<th style=\"%s\">%s</th>" % (th_style, title)
        table_body = ""
        for row in size_model["sizeAttr"]["list"]:
            table_body += "<tr>"
            for element in row:
                table_body += "<td style=\"%s\">%s</td>" % (td_style, element)
            table_body += "</tr>"
        table_body += "<tr><td style=\"%s\" colspan=\"%d\"><img src=\"%s\" style=\"%s\"></td></tr>" % (
            "border:1px solid #e0e0e0;",
            len(size_model["sizeAttr"]["title"]),
            size_model["url"], im_style
        )
        table_head = "<tr>%s</tr>" % table_head
        return table_html % (tb_style, table_head, table_body)

    @classmethod
    def compute_discount(cls, s_price, t_price):
        s_price, t_price = float(s_price), float(t_price)
        if s_price <= t_price:
            return 0
        times = round(t_price / s_price, 2)
        return int((1-times)*100)

    @classmethod
    def clear_quote(cls, product_sku):
        for sku in product_sku:
            sku_price = sku["skuVal"]["skuPrice"]
            sku["skuVal"]["skuPrice"] = sku_price.replace(",", "")
            if not sku["skuVal"].get("skuBulkPrice"):
                continue
            bulk_price = sku["skuVal"]["skuBulkPrice"]
            sku["skuVal"]["skuBulkPrice"] = bulk_price.replace(",", "")

    def export_product(self):
        ali_tag = self._category()
        with sessionCM() as session:
            category = Category.find_by_site_tag(session, self.site.id, ali_tag)
        if category:
            self.product["CategoryUID"] = category.id
            self.product["Category"]["ID"] = ali_tag
            self.product["Category"]["Name"] = FeedTemplate.get_category_group(category.id)
            self.specifics = self.spec_entry.get({"CategoryUID": category.id})
            self.product["ProductSpecifics"] = self._specifics()
        self.product["Title"] = self._title()
        self.product["Description"] = self._description()
        self.product["PictureURLs"] = self._pictures()
        self.product["GrossWeight"] = self._gross_weight()
        self.product["SourceInfo"] = self.source_info
        self.product["ListingType"] = "FixedPriceItem"
        self.product["ListingDuration"] = "30"
        self.product["DispatchTimeMax"] = "7"
        self.product["StartPrice"] = self._start_price()
        self.product.update(self._product_unit())
        self.product.update(self._package_size())
        self.product.update(self._product_sku())
        self.product["ParentSKU"] = self.gen_parent_sku() if self.product["ProductSKUs"] else ""
        return self.product
