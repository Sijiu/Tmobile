# coding:utf-8

import sqlalchemy as SA
from lib.model.session import sessionCM
from lib.model.base import Base
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound


class LagouFirst(Base):

    __tablename__ = "lagou_first"
    id = SA.Column(SA.INTEGER, primary_key=True, autoincrement=True)
    company = SA.Column(SA.String(128))
    job_name = SA.Column(SA.String(128))  # max = 21845ring
    publish_time = SA.Column(SA.String(16))
    salary = SA.Column(SA.String(12))
    city = SA.Column(SA.String(12))
    exp = SA.Column(SA.String(24))
    edu_back = SA.Column(SA.String(24))
    job_type = SA.Column(SA.String(8))
    job_require = SA.Column(SA.TEXT)
    company_address = SA.Column(SA.String(128))
    company_url = SA.Column(SA.String(256))
    hr_site = SA.Column(SA.String(16))


    @classmethod
    def create(cls, session, company, job_name, publish_time, salary, city, exp, edu_back, job_type, job_require, company_address,
               company_url, hr_site,):
            lagou_first = LagouFirst()
            lagou_first.company = company
            lagou_first.job_name = job_name
            lagou_first.publish_time = publish_time
            lagou_first.salary = salary
            lagou_first.city = city
            lagou_first.exp = exp
            lagou_first.edu_back = edu_back
            lagou_first.job_type = job_type
            lagou_first.job_require = job_require
            lagou_first.company_address = company_address
            lagou_first.company_url = company_url
            lagou_first.hr_site = hr_site
            session.add(lagou_first)
            session.commit()
            return lagou_first

