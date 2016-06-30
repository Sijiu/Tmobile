# --coding:utf-8

from urllib2 import urlopen
from bs4 import BeautifulSoup
from wikisql import Wiki_first
from lib.model.session import sessionCM
import ujson as json
import re
pages = set()


class Lagou(object):

    def getlinks(self, page_url):
        global pages
        real_url = "http://www.lagou.com" + page_url
        print real_url
        html = urlopen(real_url)
        bs_obj = BeautifulSoup(html)
        # print "---", bs_obj
        flag = ""
        p = bs_obj.p.get_text()
        try:
            json_info = json.loads(p)
            print "json===", json_info
            # print "content--", len(json.loads(p))
            result = json_info["content"]["positionResult"]["result"]
            self.get_company_links(result)
        except AttributeError:
            flag = "wrong"
            print "页面缺少一些属性，不过不用太担心！"
        except IndexError:
            flag = "wrong"
            print "list index out of range, content"
        # try:
        #     with sessionCM() as session:
        #         print "---", flag, len(flag)
        #         if not len(flag):
        #             Wiki_first.create(session, h1=h1, content=content, edit=edit, url=real_url)
        #             print "pages insert"
        #         else:
        #             Wiki_first.create(session, h1="", content="The page is missing something, Don't worry!"
        #                               , edit="", url=real_url)
        #             print "notes insert"
        # except Exception:
        #     print "Insert Failed!"
        # bslink = bs_obj.findAll("a", href = re.compile("^(/wiki/)"))
        # for link in bslink:
        #     if "href" in link.attrs:
        #         if link.attrs["href"] not in pages:
        #             # 我们遇到了新的页面
        #             new_page = link.attrs["href"]
        #             print "-"*15, "\nnewPage==", new_page
        #             pages.add(new_page)
        #             # getlinks(new_page)

    def get_company_links(self, company_list):
        company_links = []
        link_front = "http://www.lagou.com"
        link_behind = ".html"
        for i in range(len(company_list)):
            print "%s----%s" % (i, company_list[i])
            company_id = company_list[i]["companyId"]
            print "%s--id--%s" % (i, company_id)
            company_links.append(link_front + str(company_id) + link_behind)
        print "---", company_links
        print "edit--",
        # bs_obj = []
        # job_bt = bs_obj.find(class_="job_bt").findAll("p")[0]
        # print "EEEEE===", job_bt


if __name__ == "__main__":
    la_gou = Lagou()
    # getlinks('/wiki/User:Yhz1221')
    # getlinks('/wiki/Scrapy')
    la_gou.getlinks('/jobs/positionAjax.json?gj=3%E5%B9%B4%E5%8F%8A%E4%BB%A5%E4%B8%8B&px=default&city=%E5%8C%97%E4%BA%AC&needAddtionalResult=false')
    # getlinks('/jobs/1283333.html')
