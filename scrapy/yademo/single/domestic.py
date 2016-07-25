# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/11/26
# @description: 

import random
import requests
from furion.lib.utils.currency_util import get_rate


class DomesticLink(object):

    ROUTER = [
        "http://119.255.38.138:9400",
        "http://119.255.38.138:9401",
        "http://119.255.38.138:9402",
        "http://119.255.38.138:9403",
        "http://119.255.38.140:9400",
        "http://119.255.38.140:9401",
        "http://119.255.38.140:9402",
        "http://119.255.38.140:9403",
        "http://119.255.38.141:9400",
        "http://119.255.38.141:9401",
        "http://119.255.38.141:9402",
        "http://119.255.38.141:9403",
    ]

    def __init__(self, url, platform):
        self.url = url
        self.platform = platform
        self.router = random.choice(self.ROUTER)
        self.rate = get_rate("CNY", "USD")

    def export_product(self):
        request_url = "%s/collect/%s/" % (self.router, self.platform)
        params = {
            "url": self.url,
            "rate": self.rate
        }
        res = requests.post(request_url, params, timeout=10)
        response = res.json()
        if not response.get("success"):
            raise Exception
        return response["feed"]