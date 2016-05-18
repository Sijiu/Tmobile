# --coding:utf-8

from urllib2 import urlopen
from bs4 import  BeautifulSoup
import re

pages = set()
def getlinks(pageUrl):
    global pages
    html = urlopen("https://zh.wikipedia.org" + pageUrl)
    bsObj = BeautifulSoup(html)
    try:
        print "h1---", bsObj.h1.get_text()
        print "content--", bsObj.find(id="mw-content-text").findAll("p")[0]
        print "edit--", bsObj.find(id="ca-edit").find("span").find("a").attrs["href"]
    except AttributeError:
        print "页面缺少一些属性，不过不用太担心！"

    bslink = bsObj.findAll("a", href = re.compile("^(/wiki/)"))
    for link in bslink:
        if "href" in link.attrs:
            if link.attrs["href"] not in pages:
                # 我们遇到了新的页面
                newPage = link.attrs["href"]
                print "-"*15, "\nnewPage==", newPage
                pages.add(newPage)
                getlinks(newPage)

getlinks('/wiki/網路蜘蛛')