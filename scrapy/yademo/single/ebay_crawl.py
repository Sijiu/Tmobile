# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/6/17
# @description:


import re
from furion.lib.model.category import Category
from furion.lib.model.session import sessionCM
from furion.lib.handlers.feed_template import FeedTemplate
from furion.lib.handlers.template import generate_template
from furion.lib.handlers.trading_handler import TradingHandler
from furion.lib.nosql.redis_util import RedisUtil
from furion.lib.utils.currency_util import transform


class EbayLink(object):

    def __init__(self, url, site):
        self.url = url
        self.site = site
        self.product = generate_template()
        self.item_id = self._extract_id()

    def _extract_id(self):
        zz_str = r"(\d{12})"
        pattern = re.compile(zz_str)
        result = pattern.findall(self.url)
        if not result:
            return None
        return result[0]

    @property
    def source_info(self):
        return dict(
            SiteID=self.site.id,
            Site=self.site.name,
            Platform="eBay",
            Link=self.url,
            ProductID=self.item_id
        )

    def export_product(self):
        trading_handler = TradingHandler(
            site_id=self.site.tag,
            environment="production"
        )
        item = trading_handler.retrieve_item(self.item_id)
        feed = item["Item"]
        feed["Status"] = ""
        feed["Description"] = re.sub(r'<script[\S\s]*?</script>|\n', '', feed["Description"])
        if feed["ListingDuration"] == "GTC":
            feed["ListingDuration"] = "0"
        else:
            feed["ListingDuration"] = feed["ListingDuration"].replace("Days_", "")
        ft = FeedTemplate(self.site.id)
        with sessionCM() as session:
            category = Category.find_by_site_tag(
                session, self.site.id, feed["PrimaryCategory"]["CategoryID"])
        self.product = ft.import_from_ebay(feed, category.id)
        self.product["SourceInfo"] = self.source_info
        price = float(self.product["StartPrice"])
        self.product["StartPrice"] = transform(self.site.currency, "USD", price)
        for variation in self.product["ProductSKUs"]:
            variation["Price"] = transform(self.site.currency, "USD", price)
        return self.product