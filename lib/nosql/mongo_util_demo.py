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
# db.authenticate(settings.mongo_user, settings.mongo_password)
fs = GridFS(db, collection='picture')
fs_conn = db.picture.files


class ServerFS(object):
    def __init__(self):
        self.gfs = fs
        self.conn = fs_conn

    def save(self, content, **kwargs):
        im_fd = StringIO(content)
        im = Image.open(im_fd)
        im.thumbnail(im.size, Image.ANTIALIAS)
        kwargs["size"] = "%d*%d" % im.size
        kwargs["filename"] = self.gen_picture_name()
        im_obj = StringIO()
        im.save(im_obj, "JPEG")
        im_obj.seek(0)
        file_id = self.gfs.put(im_obj.read(), **kwargs)
        im_obj.close()
        im_fd.close()
        return file_id

    def modify(self, condition, doc, upsert=False, multi=False):
        self.conn.update(condition, doc, upsert=upsert, multi=multi)

    def insert(self, content, **kwargs):
        file_id = self.gfs.put(content, **kwargs)
        return file_id

    def find(self, skip=0, limit=0, **kwargs):
        if limit:
            ps = self.conn.find(kwargs).skip(skip).limit(limit).sort("uploadDate", pymongo.DESCENDING)
            return ps
        else:
            return self.conn.find(kwargs).skip(skip).sort("uploadDate", pymongo.DESCENDING)

    def delete(self, file_id):
        # 注意file_id是_id的值，ObjectId类型的，不是字典
        # 是ObjectId("5561d31cace2570221226d30")
        # 不是{"_id": ObjectId("5561d31cace2570221226d30")}
        return self.gfs.delete(ObjectId(file_id))

    def get_count(self, **kwargs):
        return self.conn.find(kwargs).count()

    def get(self, file_id):
        return self.gfs.get(ObjectId(file_id))

    @classmethod
    def gen_picture_name(cls, length=8):
        chars = lowercase + digits
        random_str = "".join([random.choice(chars) for i in xrange(length)])
        return random_str + "." + "jpg"

    def delete_by_shop(self, shop_id):
        pictures = self.conn.find({"shop_id": shop_id})
        for picture in pictures:
            self.gfs.delete(ObjectId(picture["_id"]))
        return self.conn.remove({"shop_id": shop_id})


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

server_fs = ServerFS()