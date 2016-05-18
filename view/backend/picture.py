# -*- coding: utf-8 -*-


# -*- coding: utf-8 -*-

# @author: GeFei
# @date: 15/12/11
# @description:

import datetime
import traceback
from PIL import Image
import requests
import ujson as json
import base64
from bson import ObjectId
from furion.config import settings
from furion.controls.picture.watermark import WaterMark
from furion.lib.utils.logger_util import logger
from furion.lib.model.session import sessionCM
from furion.views.backend.shop import ShopHandler
from furion.lib.nosql.mongo_util import server_fs
from furion.lib.model.user_property import UserProperty
from tornado.web import MissingArgumentError, authenticated


class PictureHandler(ShopHandler):

    @authenticated
    def get(self, *args, **kwargs):
        user = self.get_current_user()
        method_route = {
            "display": self.display_my_picture,
        }
        try:
            category = args[0]
            result = method_route[category](user.id)
            render_settings = result[1]
            render_settings["authority"] = self.current_user.authority
            self.render(result[0], **render_settings)
        except Exception, e:
            logger.error(traceback.format_exc(e))
            self.render("500.html")

    @authenticated
    def post(self, *args, **kwargs):
        user = self.get_current_user()
        method_route = {
            "delete": self.delete_picture,
            "group/add": self.add_group,
            "group/del": self.del_group,
            "group/rename": self.rename_group,
            "group/move": self.move_picture,
            "group/pic": self.display_group_picture,
            "search": self.search_pictures,
            "filter": self.filter_pictures,
            "modal": self.modal_image,
            "upload/local": self.upload_local_image,
            "upload/net": self.upload_net_image,
            "upload/base": self.upload_base_image,
            "watermark": self.add_water_mark
        }
        try:
            category = args[0]
            result = method_route[category](user.id)
            self.write(result)
        except Exception, e:
            logger.error(traceback.format_exc(e))
            self.render("500.html")

    def modal_image(self, user_id):
        render_settings = self.display_my_picture(user_id)[1]
        render_settings["status"] = 1
        return render_settings

    def add_group(self, user_id):
        group_value = self.params.get("group_value")
        with sessionCM() as session:
            UserProperty.add_pic_group(session, user_id, group_value)
        return {
            "status": 1,
            "message": "This new group has been added well"
        }

    def del_group(self, user_id):
        group_value = json.loads(self.params.get("group_value"))
        group_id = json.loads(self.params.get("group_id"))
        with sessionCM() as session:
            for i in group_value:
                UserProperty.delete_pic_group(session, user_id, i)
        server_fs.modify({"user_id": user_id, "group_id": {"$in": group_id}}, {"$set": {"group_id": "tree_0"}}, False, True)
        return {
            "status": 1,
            "message": "该分组已成功删除，分组下图片移入回收站中。"
        }

    def rename_group(self, user_id):
        group_value = self.params.get("group_value")
        new_value = self.params.get("new_value")
        with sessionCM() as session:
            UserProperty.rename_pic_group(session, user_id, group_value, new_value)
            UserProperty.rename_pic_group(session, user_id, group_value, new_value)
        return {
            "status": 1,
            "message": "This group has been renamed well"
        }

    def delete_picture(self, user_id):
        pic_id = self.params.get("pic_id")
        del_type = self.params.get("del_type")
        pic_id = json.loads(pic_id)
        obj_id = []
        for i in pic_id:
            obj_id.append(ObjectId(i))
        if del_type == "temp":
            server_fs.modify({"_id": {"$in": obj_id}}, {"$set": {"group_id": "tree_0"}}, False, True)
        elif del_type == "complete":
            for j in obj_id:
                server_fs.delete(j)
        return {
            "status": 1
        }

    def move_picture(self, user_id):
        render_settings = dict()
        new_id = self.params.get("new_id")
        pic_id = self.params.get("pic_id")
        pic_id = json.loads(pic_id)
        obj_id = []
        for i in pic_id:
            obj_id.append(ObjectId(i))
        server_fs.modify({"_id": {"$in": obj_id}}, {"$set": {"group_id": new_id}}, False, True)
        render_settings["status"] = 1
        render_settings.update(self.picture_by_page(user_id, new_id, 0, ""))
        return render_settings

    def upload_net_image(self, user_id):
        used_space = self.used_space_count(user_id)
        if used_space < 1000:
            group_id = self.params.get("group_id") or "tree_1"
            picture_urls = self.params.get("picture_urls")
            picture_urls = json.loads(picture_urls)
            dealt_status = {
                "total": len(picture_urls),
                "success": 0,
                "error": 0
            }
            for picture_url in picture_urls:
                picture = self.get_picture(picture_url)
                if not picture:
                    dealt_status["error"] += 1
                    continue
                meta = dict(
                    content_type=picture.headers["Content-Type"],
                    user_id=user_id,
                    group_id=group_id,
                    quote_status=0
                )
                server_fs.save(picture.content, **meta)
                dealt_status["success"] += 1
            render_settings = dict()
            render_settings["status"] = 1
            render_settings["message"] = "共上传了%(total)d张图片\n成功:%(success)d张\n失败:%(error)d张" % dealt_status
            render_settings.update(self.picture_by_page(user_id, group_id, 0, ""))
        else:
            render_settings = dict()
            render_settings["status"] = 1
            render_settings["message"] = "图片空间已满"
        return render_settings

    def extract_display_info(self, user_id, pictures):
        results = list()
        protocol = "https" if settings.execute_env == "production" else "http"
        for picture in pictures:
            i = dict(
                Link="%s://%s/image/%s/%s.%s" % (
                    protocol, self.request.host, user_id,
                    str(picture["_id"]), "jpg"
                ),
                Name=picture["filename"],
                Id=str(picture["_id"]),
                Size=picture["size"],
                Length="%.1fK" % (picture["length"]/1024.0)
            )
            results.append(i)
        return results

    @staticmethod
    def gen_col_map(pic_length):
        col_map = dict()
        quotient = pic_length / 6
        remainder = pic_length % 6
        for col in range(0, 6):
            col_map[col] = quotient
        for r in range(0, remainder):
            col_map[r] += 1
        return col_map

    def picture_by_page(self, user_id, group_id, out_len, out_pictures):
        try:
            page_n = self.params.get("page_n") or 50
            page_n = int(page_n)
            if page_n not in [30, 50, 100]:
                page_n = 50
        except MissingArgumentError:
            page_n = 50
        except ValueError:
            page_n = 50
        try:
            c_page = self.params.get("c_page") or 1
            c_page = int(c_page)
            if c_page <= 0:
                c_page = 1
        except MissingArgumentError:
            c_page = 1
        except ValueError:
            c_page = 1
        start = (c_page-1)*page_n
        if group_id == "all_group":
            ps_len = out_len or server_fs.get_count(user_id=user_id, group_id={"$exists": True, "$ne": "tree_0"})
            pictures = out_pictures or server_fs.find(start, page_n, user_id=user_id, group_id={"$exists": True, "$ne": "tree_0"})
        else:
            ps_len = out_len or server_fs.get_count(user_id=user_id, group_id=group_id)
            pictures = out_pictures or server_fs.find(start, page_n, user_id=user_id, group_id=group_id)
        page_total = ps_len/page_n + 1 if ps_len % page_n > 0 else ps_len/page_n
        page = page_total if c_page >= page_total else c_page
        render_settings = {
            "pictures": self.extract_display_info(user_id, pictures),
            "pages": self.gen_page(page_total, 5, page),
            "page_total": page_total,
            "page_n": page_n,
            "c_page": c_page,
            "status": 1,
            "ps_len": ps_len,
            "col_map": self.gen_col_map(
                page_n if ps_len >= start + page_n else ps_len - start
            )
        }
        return render_settings

    def display_group_picture(self, user_id):
        group_id = self.params.get("group_id")
        render_settings = dict()
        render_settings["status"] = 1
        if group_id:
            render_settings.update(self.picture_by_page(user_id, group_id, 0, ""))
        else:
            ps_len = server_fs.get_count(user_id=user_id, group_id={"$exists": True, "$ne": "tree_0"})
            pictures = server_fs.find(user_id=user_id, group_id={"$exists": True, "$ne": "tree_0"})
            render_settings.update(self.picture_by_page(user_id, "", ps_len, pictures))
        return render_settings

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

    def search_pictures(self, user_id):
        try:
            page_n = self.params.get("page_n") or 50
            page_n = int(page_n)
            if page_n not in [30, 50, 100]:
                page_n = 50
        except MissingArgumentError:
            page_n = 50
        except ValueError:
            page_n = 50
        try:
            c_page = self.params.get("c_page") or 1
            c_page = int(c_page)
            if c_page <= 0:
                c_page = 1
        except MissingArgumentError:
            c_page = 1
        except ValueError:
            c_page = 1
        start = (c_page-1)*page_n
        p_title = self.params.get("pic_title")
        group_id = self.params.get("group_id")
        if group_id == "all_group":
            ps_len = server_fs.get_count(user_id=user_id, group_id={"$exists": True, "$ne": "tree_0"}, filename={"$regex": '.*'+p_title+'.*', "$options": "$i"})
            pictures = server_fs.find(start, page_n, user_id=user_id, group_id={"$exists": True, "$ne": "tree_0"}, filename={"$regex": '.*'+p_title+'.*', "$options": "$i"})
        else:
            ps_len = server_fs.get_count(user_id=user_id, group_id=group_id, filename={"$regex": '.*'+p_title+'.*', "$options": "$i"})
            pictures = server_fs.find(start, page_n, user_id=user_id, group_id=group_id, filename={"$regex": '.*'+p_title+'.*', "$options": "$i"})
        render_settings = dict()
        render_settings["status"] = 1
        render_settings.update(self.picture_by_page(user_id, group_id, ps_len, pictures))
        return render_settings

    def filter_pictures(self, user_id):
        try:
            page_n = self.params.get("page_n") or 50
            page_n = int(page_n)
            if page_n not in [30, 50, 100]:
                page_n = 50
        except MissingArgumentError:
            page_n = 50
        except ValueError:
            page_n = 50
        try:
            c_page = self.params.get("c_page") or 1
            c_page = int(c_page)
            if c_page <= 0:
                c_page = 1
        except MissingArgumentError:
            c_page = 1
        except ValueError:
            c_page = 1
        start = (c_page-1)*page_n
        group_id = self.params.get("group_id")
        start_time = self.params.get("start_time") + " 00:00:00"
        end_time = self.params.get("end_time") + " 23:59:59"
        start_time = datetime.datetime.strptime(start_time, "%Y-%m-%d %H:%M:%S")
        end_time = datetime.datetime.strptime(end_time, "%Y-%m-%d %H:%M:%S")
        p_title = self.params.get("pic_title")
        if p_title:
            if group_id == "all_group":
                ps_len = server_fs.get_count(user_id=user_id, uploadDate={"$gte": start_time,"$lt": end_time}, filename={"$regex": '.*'+p_title+'.*', "$options": "$i"})
                pictures = server_fs.find(start, page_n, user_id=user_id, uploadDate={"$gte": start_time,"$lt": end_time}, filename={"$regex": '.*'+p_title+'.*', "$options": "$i"})
            else:
                ps_len = server_fs.get_count(user_id=user_id, group_id=group_id, uploadDate={"$gte": start_time,"$lt": end_time}, filename={"$regex": '.*'+p_title+'.*', "$options": "$i"})
                pictures = server_fs.find(start, page_n, user_id=user_id, group_id=group_id, uploadDate={"$gte": start_time,"$lt": end_time}, filename={"$regex": '.*'+p_title+'.*', "$options": "$i"})
        else:
            if group_id == "all_group":
                ps_len = server_fs.get_count(user_id=user_id, uploadDate={"$gte": start_time,"$lt": end_time})
                pictures = server_fs.find(start, page_n, user_id=user_id, uploadDate={"$gte": start_time,"$lt": end_time})
            else:
                ps_len = server_fs.get_count(user_id=user_id, group_id=group_id, uploadDate={"$gte": start_time, "$lt": end_time})
                pictures = server_fs.find(start, page_n, user_id=user_id, group_id=group_id, uploadDate={"$gte": start_time, "$lt": end_time})
        render_settings = dict()
        render_settings["status"] = 1
        render_settings.update(self.picture_by_page(user_id, "", ps_len, pictures))
        return render_settings

    def sort_pictures(self, user_id):
        pass

    def upload_local_image(self, user_id):
        protocol = "https" if settings.execute_env == "production" else "http"
        used_space = self.used_space_count(user_id)
        if used_space < 1000:
            group_id = self.params.get("group_id") or "tree_1"
            pictures = self.request.files.get("Filedata") or self.request.files.get("imgFile") or self.request.files["picture"]
            success, error, urls = 0, 0, list()

            for picture in pictures:
                try:
                    meta = dict(
                        filename=picture["filename"],
                        content_type="image/jpeg",
                        user_id=user_id,
                        group_id=group_id,
                        quote_status=0
                    )
                    content = picture["body"]
                    _id = server_fs.save(content, **meta)
                    urls.append("%s://%s/image/%s/%s.%s" % (
                        protocol, self.request.host, user_id,
                        str(_id), "jpg"
                    ))
                    success += 1
                except Exception, e:
                    logger.error(traceback.format_exc(e))
                    error += 1
            render_settings = dict()
            render_settings["status"] = 1
            render_settings.update(self.picture_by_page(user_id, group_id, 0, ""))
            return {
                "render_settings": render_settings,
                "success": success,
                "error": error,
                "url": ";".join(urls)
            }
        else:
            return {
                "status": 1,
                "success": 0,
                "error": 0,
                "url": ";".join({})
            }

    def upload_base_image(self, user_id):
        protocol = "https" if settings.execute_env == "production" else "http"
        file_data = self.params.get("filedata")
        data_id = self.params.get("data_id", "")
        data_name = self.params.get("data_name", "")
        picture = base64.b64decode(file_data)
        success, error, urls = 0, 0, list()
        if data_id == "":
            group_id = "tree_1"
        else:
            group_id = server_fs.find(_id=ObjectId(data_id))[0]["group_id"]
        try:
            meta = dict(
                filename=data_name,
                content_type="image/jpeg",
                user_id=user_id,
                group_id=group_id
            )
            if data_id != "":
                server_fs.delete(data_id)
            _id = server_fs.save(picture, **meta)
            cropper_pic = server_fs.find(_id=ObjectId(_id))
            for pic in cropper_pic:
                length = "%.1fK" % (pic["length"]/1024.0)
                size = pic["size"]
            urls.append("%s://%s/image/%s/%s.%s" % (
                protocol, self.request.host, user_id,
                str(_id), "jpg"
            ))
            success += 1
        except Exception, e:
            logger.error(traceback.format_exc(e))
            error += 1
        return {
            "status": 1,
            "success": success,
            "error": error,
            "url": ";".join(urls),
            "length": length,
            "size": size,
            "id": str(_id)
        }

    def add_water_mark(self, user_id):
        main_image_str = self.params.get("main_image")
        mark_txt = self.params.get("mark_txt")
        position = self.params.get("position") or "mb"
        if not (mark_txt and main_image_str):
            return {
                "status": 0, "message": "参数不全导致的错误"
            }
        image_ids = json.loads(main_image_str)
        success, error = 0, 0
        for image_id in image_ids:
            try:
                image_buffer = server_fs.get(image_id)
                image = Image.open(image_buffer)
                meta = server_fs.conn.find_one({"_id": ObjectId(image_id)})
                handler = WaterMark(image, txt=mark_txt, layout=position)
                new_image = handler.water_mark()
                server_fs.delete(image_id)
                server_fs.insert(new_image, **meta)
                success += 1
            except Exception, e:
                logger.info(traceback.format_exc(e))
                error += 1
        return {"status": 1, "success": success, "error": error}

    def display_my_picture(self, user_id):

        render_settings = dict()
        re_group = []
        with sessionCM() as session:
            pic_group = UserProperty.get_pic_group(session, user_id)
        for i in pic_group:
            re_group.append(i.value)
        render_settings["pic_group"] = json.dumps(re_group)
        used_space = self.used_space_count(user_id)
        render_settings["used_space"] = "%.2fM" % used_space
        render_settings["user_id"] = user_id
        return "index/mypic.html", render_settings

    @staticmethod
    def used_space_count(user_id):
        pictures = server_fs.find(0, 0, user_id=user_id, group_id={"$exists": True, "$ne": "tree_0"})
        used_space = 0
        if pictures:
            for pic in pictures:
                used_space += pic["length"]/1024.0/1024.0
        return used_space







