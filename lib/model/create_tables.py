# -*- coding: utf-8 -*-

from lib.model.base import metadata, db
from scrapy.wikisql import Wiki_first


class CreateTables(object):
    @classmethod
    def create_tables(cls):
        metadata.create_all(db)

print "sss====", CreateTables.create_tables()
