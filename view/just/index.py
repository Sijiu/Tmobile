# -*- coding: utf-8 -*-
import tornado
import tornado.web


class WriteHandler(tornado.web.RequestHandler):
    def get(self):
        greeting = self.get_argument('greeting',  "hello")
        self.write(greeting + ', friendly user!')
        # self.render("test.html")


class TestHandler(tornado.web.RequestHandler):
    def get(self):
        hello = "Oh, Help me!"
        self.render("test.html", hello=hello)


class IndexHandler(tornado.web.RequestHandler):
    def get(self):
        self.render("index.html")
