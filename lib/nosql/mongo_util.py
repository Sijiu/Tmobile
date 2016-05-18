# -*- coding: utf-8 -*-

import datetime
import random
import pymongo
from cStringIO import StringIO
from string import lowercase, digits
from PIL import Image
from bson import ObjectId
from pymongo.errors import DuplicateKeyError
from gridfs import GridFS
from config import settings


conn = pymongo.MongoClient(host=settings.mongo_host, port=settings.mongo_port)

db = conn['furion']

class FeedsWarehouse(object):
    def __init__(self, project_name):
        collections = db.collection_names()
        if project_name.startswith("fw") and project_name not in collections:
            db.create_collection(project_name)
            db[project_name].ensure_index([("SourceInfo.ProductID", pymongo.ASCENDING)], unique=True)
            db[project_name].ensure_index([("CategoryUID", pymongo.ASCENDING)])
            db[project_name].ensure_index([("update_time", pymongo.DESCENDING)])
        if project_name.startswith("fb") and project_name not in collections:
            db.create_collection(project_name)
            db[project_name].ensure_index([("update_time", pymongo.DESCENDING)])
        self.conn = db[project_name]

    def save(self, doc):
        doc["create_time"] = doc.get("create_time") or datetime.datetime.now()
        doc["update_time"] = doc.get("update_time") or datetime.datetime.now()
        try:
            return self.conn.insert(doc)
        except DuplicateKeyError:
            src_pid = doc["SourceInfo"]["ProductID"]
            if src_pid == "":
                doc["SourceInfo"]["ProductID"] = self.gen_random_digits()
            else:
                self.conn.remove({"SourceInfo.ProductID": src_pid})
            return self.conn.insert(doc)

    def get(self, kwargs, *field):
        fields = dict()
        for fi in field:
            fields[fi] = True
        if fields:
            return self.conn.find_one(kwargs, fields)
        else:
            return self.conn.find_one(kwargs)

    def get_condition(self, kwargs, field):
        return self.conn.find_one(kwargs, field)

    def get_all(self, kwargs, *field):
        fields = dict()
        for fi in field:
            fields[fi] = True
        if fields:
            return self.conn.find(kwargs, fields)
        else:
            return self.conn.find(kwargs)

    def modify(self, kwargs, doc, upsert=False, multi=False):
        update_time = datetime.datetime.now()
        if "$set" in doc:
            doc["$set"]["update_time"] = update_time
        else:
            doc["update_time"] = update_time
        try:
            return self.conn.update(kwargs, doc, upsert=upsert, multi=multi)
        except DuplicateKeyError, e:
            src_pid = doc["SourceInfo"]["ProductID"]
            if src_pid == "":
                doc["SourceInfo"]["ProductID"] = self.gen_random_digits()
            else:
                self.conn.remove({"SourceInfo.ProductID": src_pid})
            return self.conn.insert(doc)

    def delete(self, kwargs):
        return self.conn.remove(kwargs)

    def skip_limit(self, kwargs, skip=0, limit=0):
        return self.conn.find(kwargs).sort("update_time", pymongo.DESCENDING)\
            .skip(skip).limit(limit)

    def get_distinct(self, field):
        return self.conn.distinct(field)

    def get_count(self, kwargs):
        return self.conn.find(kwargs).count()

    def group_by(self, key, condition, initial, reduce):
        return self.conn.group(key, condition, initial, reduce)

    def drop(self):
        return self.conn.drop()

    @classmethod
    def gen_random_digits(cls):
        id_str = "".join([random.choice(digits) for i in xrange(10)])
        return "".join(["AC", id_str])
