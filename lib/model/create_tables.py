# -*- coding: utf-8 -*-

from model.base import metadata, db
from model.amazon_errcode import Amazon_errcode


class CreateTables(object):
    @classmethod
    def create_tables(cls):
        metadata.create_all(db)

print "sss====", CreateTables.create_tables()
