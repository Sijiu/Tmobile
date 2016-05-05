#coding:UTF-8
import datetime
from sqlalchemy import Column, String, create_engine, DateTime, Integer
from sqlalchemy.orm import sessionmaker
from sqlalchemy.ext.declarative import declarative_base

# 创建对象的基类：
Base = declarative_base()
# 定义user对象


class User(Base):
    __tablename__ = 'user_first'
    # 表的结构
    id = Column(String(20), primary_key=True)
    username = Column(String(20))


class Book(Base):
    __tablename__ = 'book'
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(20))


class Pluralpoem(Base):
    __tablename__ = 'pluralpoem'
    id = Column(Integer, primary_key=True, autoincrement=True)
    title = Column(String(30))
    create_time = Column(DateTime, default=datetime.datetime.now)
# 初始化数据库连接
# db = SA.create_engine(
#     "mysql://%s:%s@%s/%s?charset=utf8" % (db_info["user"], db_info["password"], db_info["host"], db_info["db_name"]),
engine = create_engine("mysql://%s:%s@%s/%s" % ("", "", "45.78.57.254", "poem"))
#  engine = create_engine('mysql://root:1111@localhost/test')
# 创建DBsession类型：
DBSession = sessionmaker(bind=engine)

# # 创建session
# session = DBSession()
# # 创建Query查询，filter是where查询条件，最后调用one()返回唯一行，如果调用all()就返回所有行
# poem = session.query(Pluralpoem).filter(Pluralpoem.id == 1).one()
#
# all_poem = session.query(Pluralpoem).filter().all()
# # 打印类型和对象的name属性
# print 'type==', type(poem), ",title:", poem.title
# for i in all_poem:
#     print i.id, "username:", i.title, i.create_time
#
# # 关闭session
# session.close()

# 创建session对象:
session = DBSession()
# 创建新User对象:
new_poem = Pluralpoem(title='Shake Bianco', create_time=datetime.datetime.now())
# 添加到session:
session.add(new_poem)
# 提交即保存到数据库:
session.commit()
print new_poem.id, "is insert completely."
# 关闭session:
session.close()




