# -*- coding: utf-8 -*-

import os
import tornado.httpserver
import tornado.ioloop
import tornado.options
import tornado.web
from view.just.index import IndexHandler, TestHandler, WriteHandler
from tornado.options import define, options

from view.just.poem import PoemPageHandler, PoemListHandler

define("port", default=8888, help="run on the given port", type=int)


SETTINGS = dict(
    template_path=os.path.join(os.path.dirname(__file__), "templates"),
    static_path=os.path.join(os.path.dirname(__file__), "static")
)

urls = [
            (r"/", IndexHandler),
            (r"/write", WriteHandler),
            (r"/test", TestHandler),
            (r"/poem", PoemPageHandler),
            (r"/list", PoemListHandler),
            (r"/picture/", PoemListHandler),
        ]


if __name__ == "__main__":
    print 'Development server running on "http://localhost:8888"'
    tornado.options.parse_command_line()
    app = tornado.web.Application(
        handlers=urls,
        debug=True,
        **SETTINGS
    )
    http_server = tornado.httpserver.HTTPServer(app)
    http_server.listen(options.port)
    tornado.ioloop.IOLoop.instance().start()
