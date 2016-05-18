# -*- coding: utf-8 -*-

import os


MONGO_HOST = '127.0.0.1'
MONGO_PORT = 37017
MONGO_USER = "root"
MONGO_PASSWORD = "123456"
MAX_POOL_SIZE = 20

# log
LOG_PATH = 'E:/Project/actneed411/'
LOG_FILE = os.path.sep.join([LOG_PATH, 'furion.log'])

DEFAULT_LOG_SIZE = 1024*1024*50

# EMAIL LOGGER
LOG_MAILHOST = 'smtp.exmail.qq.com:25'
LOG_FROM = 'xxx@xxx.com'
LOG_TO = ('xxx@xxx.com', 'xxxx@163.com')
LOG_SUBJECT = 'Email for affiliate error.'
LOG_CREDENTIAL = ('xxx@xxxxx.com', 'xxxxxx')

# YAML CONFIG FILE
EBAY_YAML = "E:/Project/actneed411/ebay.yaml"
ALI_YAML = "E:/Project/actneed411/ali.yaml"
AMAZON_YAML = "E:/Project/actneed411/amazon.yaml"
WISH_YAML = "E:/Project/actneed411/wish.yaml"
LAZADA_YAML = "E:/Project/actneed411/lazada.yaml"
DHGATE_YAML = "E:/Project/actneed411/dhgate.yaml"
ENSOGO_YAML = "E:/Project/actneed411/ensogo.yaml"
JOOM_YAML = "/Users/xuhe/Project/Actneed/joom.yaml"

# mysql configure
ECHO_SQL = False

DB = {
    "user": "root",
    "password": "1111",
    "host": "127.0.0.1",
    "db_name": "test",
}

#redis configure
REDIS_HOST = "127.0.0.1"
REDIS_PORT = 6379
REDIS_DB = 0
REDIS_MAX_CONNECTIONS = 1024

#UPC_XLS_PATH
UPC_XLS_PATH = "E:/Project/actneed411/furion/static"
UPC_REQ_PATH = "E:/Project/actneed411/"

#ZIP_FILE_PATH
ZIP_FILE_PATH = "E:/Project/actneed411/"

#FONT_PATH
FONT_PATH = "E:/Project/actneed411/MSB.TTF"