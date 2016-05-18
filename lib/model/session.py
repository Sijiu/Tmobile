# -*- coding: utf-8 -*-


import contextlib
from sqlalchemy.orm import sessionmaker
from model.base import db


session_maker = sessionmaker(bind=db)


def get_session():
    """
    链接到数据库的SESSION
    """
    return session_maker()


@contextlib.contextmanager
def sessionCM():
    session = get_session()
    try:
        yield session
    except Exception, e:
        raise
    finally:
        session.close()
