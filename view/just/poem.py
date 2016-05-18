# -*- coding: utf-8 -*-

import tornado.web

from lib.nosql.mongotest import Feed


class PoemPageHandler(tornado.web.RequestHandler):
    def post(self):
        noun1 = self.get_argument('noun1')
        noun2 = self.get_argument('noun2')
        verb = self.get_argument('verb')
        noun3 = self.get_argument('noun3')
        poem = {
            "Plural": noun1,
            "Singular": noun2,
            "Verb": verb,
            "Noun": noun3
        }

        Feed("poem").save("")
        self.render('poem.html', roads=noun1, wood=noun2, made=verb, difference=noun3)


class PoemListHandler(tornado.web.RequestHandler):
    def get(self):
        print "ss==", Feed("poem").find()
        self.render("poem_list.html")

