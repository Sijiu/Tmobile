# -*- coding: utf-8 -*-
import tornado.web


class BlogHandler(tornado.web.RequestHandler):
    def get(self):
        coll = self.application.db.blog
        blog = coll.find_one()
        if blog:
            self.render("blog.html",
            page_title = blog['title'],
            blog = blog,
            )
        else:
            self.redirect('/')
