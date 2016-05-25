# -*- coding: utf-8 -*-

# @author: xuhe
# @date: 15/12/22
# @description:


class LazadaControl(object):

    ERRORS = {

    }

    def __init__(self, shop, feed):
        self.feed = feed
        self.shop_id = shop.id
        self.errors = list()

    def execute(self):
        return self.errors