# -*- coding: utf-8 -*-


import datetime

import pymongo
from pymongo import MongoClient


#client = MongoClient("10.1.15.193", 37017)
client = MongoClient("localhost", 27017)
db = client["teen"]
# print "test:", db.maxh.find_one()
# print "find,what?", db.maxh.find({"_id": "ObjectId('56946fba3a18f4867aecbcd1')"})


class Feed(object):
    def __init__(self, project_name):
        collections = db.collection_names()
        if project_name not in collections:
            db.create_collection(project_name)
            db[project_name].ensure_index(["update_time", pymongo.DESCENDING])
        self.conn = db[project_name]

    def save(self, doc):
        doc["create_time"] = doc.get("create_time") or datetime.datetime.now()
        doc["update_time"] = doc.get("update_time") or datetime.datetime.now()
        try:
            return self.conn.insert(doc)
        except EOFError:
            print "There are some errors happend!"

    def find(self, skip=0, limit=0, **kwargs):
        if limit:
            ps = self.conn.find(kwargs).skip(skip).limit(limit).sort("uploadDate", pymongo.DESCENDING)
            return ps
        else:
            return self.conn.find(kwargs).skip(skip).sort("uploadDate", pymongo.DESCENDING)
