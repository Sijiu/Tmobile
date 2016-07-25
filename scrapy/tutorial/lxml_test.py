# -*- coding: utf-8 -*-
from lxml import etree

# fp = open("pycon.html")
# text = fp.read()
# fp.close()
# html = etree.HTML(text)
# result = etree.tostring(html)
# print "--------", (result)
html = etree.parse("pycon.html")
result = etree.tostring(html, pretty_print=True)
print "sssssss==", result, type(html)
result = html.xpath('//*')
print result, "--------", len(result)
# print "============\n", result[0]
# print "------------\n", result[1]
