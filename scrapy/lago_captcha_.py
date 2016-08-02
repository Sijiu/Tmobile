# coding:utf-8
from PIL import Image
import pytesseract

try:
    print "successfully"
except ImportError:
    print '模块导入错误,请使用pip安装,pytesseract依赖以下库：'
    print 'http://www.lfd.uci.edu/~gohlke/pythonlibs/#pil'
    print 'http://code.google.com/p/tesseract-ocr/'
    raise SystemExit

image = Image.open('captcha_0.26806422253139317.jpg')
vcode = pytesseract.image_to_string(image, config='-psm 7')
print vcode
