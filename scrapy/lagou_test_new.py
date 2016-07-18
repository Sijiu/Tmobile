# -*- coding:utf-8 -*-
from urllib import urlopen
import ujson as json
import re
import math
# import pandas as pd
# from pandas import DataFrame,Series
from bs4 import BeautifulSoup


class Lagou(object):
    def lagou_spider_keyword(self, keyword):
        keyword_byte = keyword.encode('utf-8')
        keyword_index = str(keyword_byte).replace(r'\x', '%').replace(r"'", "")
        keyword_index = re.sub('^b', '', keyword_index)
        i = 0
        types = 'true'
        json_info = self.get_json_info(i, types, keyword_index)
        url_count = json_info["content"]["positionResult"]["totalCount"]
        page = int(math.ceil(url_count/15.0))
        print "\n 共有%s条，%s页" % (url_count, page)
        try:
            for i in range(page):
                if i == 0:
                    types = 'true'
                else:
                    types = 'false'
                self.get_json_info(i, types, keyword_index)
                result = json_info["content"]["positionResult"]["result"]
                print "*************第%s页--------" % (i+1)
                self.get_company_links(result)
        except AttributeError:
            flag = "wrong"
            print "页面缺少一些属性，不过不用太担心！"
        except IndexError:
            flag = "wrong"
            print "list index out of range, content"

    def get_json_info(self, i, types, keyword_index):
        url = 'http://www.lagou.com/jobs/positionAjax.json?px=default&first='+types+'&kd='+keyword_index+'&pn='+str(i+1)
        html = urlopen(url)
        print url
        bs_obj = BeautifulSoup(html)
        print "第---", bs_obj
        p = bs_obj.p.get_text()
        json_info = json.loads(p)
        print "json===", json_info
        return json_info

    def get_company_links(self, company_list):
        company_links = []
        link_front = "http://www.lagou.com/jobs/"
        link_behind = ".html"
        for i in range(len(company_list)):
            print "%s----%s" % (i, company_list[i])
            company_id = company_list[i]["companyId"]
            print "%s--id--%s" % (i, company_id)
            company_links.append(link_front + str(company_id) + link_behind)
        print "---", company_links

    def get_company_info(self, url):
        html = urlopen(url)
        print url
        bs_obj = BeautifulSoup(html)
        # print "第---", bs_obj
        h1 = bs_obj.find(id="container").h1
        print "company==", h1.find("div").get_text(), h1.attrs["title"]
        context = bs_obj.find(class_="job_request")
        salary = context.findAll("span")[0].get_text()
        city = context.findAll("span")[1].get_text()
        experience = context.findAll("span")[2].get_text()
        education_background = context.findAll("span")[3].get_text()
        off_type = context.findAll("span")[4]
        print "salary==", salary
        print "city==", city
        print "experience==", experience
        print "education_background==", education_background
        print "off_type==", off_type.get_text()
        tech_require = bs_obj.find(class_="job_bt")
        print "tech_require==", tech_require
        address = bs_obj.find(class_="work_addr")
        print "工作地址==", address.get_text().replace("\n", "").replace(" ", "")
        web_site = bs_obj.find(class_="c_feature").findAll("li")[2].a.attrs["href"]
        print "web_site==", web_site





if __name__ == "__main__":
    lagou = Lagou()
    # lagou.lagou_spider_keyword(u"兰州")
    lagou.get_company_info("http://www.lagou.com/jobs/1966817.html")
