#! /usr/bin/env python
#  -*- coding: utf-8 -*-


import urllib
import urllib2
import cookielib
import base64
import re
import json
import hashlib

cj = cookielib.LWPCookieJar()
cookie_support = urllib2.HTTPCookieProcessor(cj)
opener = urllib2.build_opener(cookie_support, urllib2.HTTPHandler)
urllib2.install_opener(opener)
postdata = {
    'entry': 'weibo',
    'gateway': '1',
    'from': '',
    'savestate': '7',
    'userticket': '1',
    'ssosimplelogin': '1',
    'vsnf': '1',
    'vsnval': '',
    'su': '',
    'service': 'miniblog',
    'servertime': '',
    'nonce': '',
    'pwencode': 'wsse',
    'sp': '',
    'encoding': 'UTF-8',
    'url': 'http://weibo.com/ajaxlogin.php?framelogin=1&callback=parent.sinaSSOController.feedBackUrlCallBack',
    'returntype': 'META'
}

def get_servertime():
    url = 'http://login.sina.com.cn/sso/prelogin.php?entry=weibo&callback=sinaSSOController.preloginCallBack&su=dW5kZWZpbmVk&client=ssologin.js(v1.3.18)&_=1329806375939'
    data = urllib2.urlopen(url).read()
    pattern = re.compile(r'"servertime":(\d*).*"nonce":"(\w*)"')
    try:
        # json_data = p.search(data).group(1)
        # json_datas = p.findall(data)
        # data = json.loads(json_datas)
        server = pattern.findall(data)
        print "---", server
        servertime = str(server[0][0])
        nonce = server[0][1]
        return servertime, nonce
    except:
        print "---ss=", pattern.findall(data)
        print 'Get severtime error!'
        return None

def get_pwd(pwd, servertime, nonce):
    pwd1 = hashlib.sha1(pwd).hexdigest()
    pwd2 = hashlib.sha1(pwd1).hexdigest()
    pwd3_ = pwd2 + servertime + nonce
    pwd3 = hashlib.sha1(pwd3_).hexdigest()
    return pwd3

def get_user(username):
    username_ = urllib.quote(username)
    username = base64.encodestring(username_)[:-1]
    return username


def login():
    username = 'zhanghao'
    pwd = 'mima'
    url = 'http://login.sina.com.cn/sso/login.php?client=ssologin.js(v1.3.18)'
    try:
        servertime, nonce = get_servertime()
    except:
        return
    global postdata
    postdata['servertime'] = servertime
    postdata['nonce'] = nonce
    postdata['su'] = get_user(username)
    postdata['sp'] = get_pwd(pwd, servertime, nonce)
    postdata = urllib.urlencode(postdata)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 6.1; WOW64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/50.0.2661.94 Safari/537.36',
        'Cookie': 'SINAGLOBAL=119.255.38.138_1463378866.628658; Apache=119.255.38.138_1463378866.628661; U_TRS1=0000008a.d02c30fc.573d3770.89e2a239; U_TRS2=0000008a.d03630fc.573d3770.faae1f19; UOR=login.sina.com.cn,login.sina.com.cn,; ULV=1463642701275:1:1:1:119.255.38.138_1463378866.628661:; SUS=SID-2306582521-1463642652-XD-swpxe-ae982ff5b1bcce512a43f27910218433; ALC=ac%3D0%26bt%3D1463642652%26cv%3D5.0%26et%3D1495178652%26uid%3D2306582521%26vf%3D0%26vs%3D0%26vt%3D0%26es%3Dd3584b85c7cf3eedb7645ec3f67664a0; ALF=1495178652; sso_info=v02m6alo5qztKWRk5ClkKOgpY6DjKWRk5SljoSYpZCjmKWRk6CljoSQpY6DpKadlqWkj5OIs4yDmLWOg4i1jKOEwA==; cREMloginname=13381491720; tgc=TGT-MjMwNjU4MjUyMQ==-1463645094-xd-A8EE553595A78CEDAA9CA7FCD15FA332; SUE=es%3D39e01fcc9a35db7d9475055a2f704467%26ev%3Dv1%26es2%3D7a72cd1584fc0ea3aec914f05372a54a%26rs0%3DOqlUNCTtX3GgWUQuf%252FF5NvU59H7QFaO1qDahKKDNQCFoDBrCsy3PVfn9tqTaHlERMmlwPtROH9Y84igauUElMKWt%252BqzbYCu9ZUPFvwyJyVqIJKKd8y8fJ9DVf%252Fi2Ro61jCxkF1PBPMDe4TwWzDgl08OTHwt3dgBxthZRosT9Mos%253D%26rv%3D0; SUP=cv%3D1%26bt%3D1463642652%26et%3D1463731494%26d%3D40c3%26i%3D8433%26us%3D1%26vf%3D0%26vt%3D0%26ac%3D0%26st%3D0%26lt%3D11%26uid%3D2306582521%26user%3D13381491720%26ag%3D1%26name%3D13381491720%26nick%3D%25E4%25B8%2583%25E5%258F%25B6%25E8%258D%2589%26sex%3D%26ps%3D0%26email%3D%26dob%3D%26ln%3D13381491720%26os%3D%26fmp%3D%26lcp%3D2012-06-19%252011%253A32%253A12; SUB=_2A256OQP2DeRxGeRN61QU-CzJyT2IHXVZT3I-rDV_PUJbstAPLXbnkW9LHeuHW1pjbhLAy-Hbvw9E7UiZC3LQ0g..; SUBP=0033WrSXqPxfM725Ws9jqgMF55529P9D9WWceC_ig6lJVVOaZz2Hvf0k5NHD95QEe05cSKnESKzp; LT=1463645094'
    }
    req = urllib2.Request(
        url = url,
        data = postdata,
        headers = headers
    )
    result = urllib2.urlopen(req)
    text = result.read()
    # p = re.compile('location\.replace\'(.∗?)\'')
    pattern_url = re.compile(r'replace\("(.*)"')
    print "text--", text.decode("gb2312").encode("utf-8")
    try:
        login_url = pattern_url.findall(text)[0]
        print login_url
        result = urllib2.urlopen(login_url)
        print "登录成功!-------------"
        # print result.read()
        success_url = 'http://weibo.com/login.php'
        success = urllib2.urlopen(success_url)
        aim_html1 = success.read()
        aim_html = unicode(aim_html1, "gb2312")
        print "---\n", aim_html.encode("utf-8")
        fp = open("sina.html", "w")
        fp.write(aim_html1)
        fp.close()
    except:
        print "text--", text
        print "text--", pattern_url.findall(text)[0]
        print 'Login error!'

login()
