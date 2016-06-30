#!/usr/bin/env python
# -*- coding: utf-8 -*-

from Tkinter import *
import urllib2, json

postid1 = '4337319110623411'

url1 = 'http://www.kuaidi100.com/query?type=yuantong&postid=%s&id=1&valicode=&temp=0.4337319110623411' % postid1

headers1 = {
    'X-Requested-With': 'XMLHttpRequest',
    'Referer': 'http://www.kuaidi100.com/?from=openv'
}


def load_data():
    html1 = urllib2.urlopen( urllib2.Request(url1, headers=headers1) ).read()
    json1 = json.loads(html1)
    list1.delete(0, END)
    for i in json1['data']:
        list1.insert(END, i['time'] + ' ' + i['context'])

frame1 = Tk()
frame1.title('快递查询 %s' % postid1)

list1 = Listbox(frame1, width=80)

list1.pack(expand=YES, fill=BOTH)

load_data()

mainloop()
