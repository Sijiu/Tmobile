# --coding:utf-8

from urllib2 import urlopen
from bs4 import BeautifulSoup
from wikisql import Wiki_first
from lib.model.session import sessionCM
import re

pages = set()
def getlinks(pageUrl):
    global pages
    real_url = "https://zh.wikipedia.org" + pageUrl
    # real_url = "https://en.wikipedia.org" + pageUrl
    html = urlopen(real_url)
    bsObj = BeautifulSoup(html)
    flag = ""
    try:
        h1 = bsObj.h1.get_text()
        content = bsObj.find(id="mw-content-text").findAll("p")[0]
        edit = bsObj.find(id="ca-edit").find("span").find("a").attrs["href"]

        print "h1---", h1
        print "content--", content
        print "edit--", edit
    except AttributeError:
        flag = "wrong"
        print "页面缺少一些属性，不过不用太担心！"
    except IndexError:
        flag = "wrong"
        print "list index out of range, content"
    try:
        with sessionCM() as session:
            print "---", flag, len(flag)
            if not len(flag):
                Wiki_first.create(session, h1=h1, content=content, edit=edit, url=real_url)
                print "pages insert"
            else:
                Wiki_first.create(session, h1="", content="The page is missing something, Don't worry!"
                                  , edit="", url=real_url)
                print "notes insert"
    except Exception:
        print "Insert Failed!"
    bslink = bsObj.findAll("a", href = re.compile("^(/wiki/)"))
    for link in bslink:
        if "href" in link.attrs:
            if link.attrs["href"] not in pages:
                # 我们遇到了新的页面
                newPage = link.attrs["href"]
                print "-"*15, "\nnewPage==", newPage
                pages.add(newPage)
                getlinks(newPage)


# getlinks('/wiki/User:Yhz1221')
# getlinks('/wiki/Scrapy')
getlinks('/wiki/Python')