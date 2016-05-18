import sqlalchemy as SA
from lib.model.session import sessionCM
from lib.model.base import Base
from sqlalchemy.orm.exc import MultipleResultsFound, NoResultFound


class Wiki_first(Base):
    __tablename__ = "wiki_first"
    id = SA.Column(SA.INTEGER, primary_key=True, autoincrement=True)
    h1 = SA.Column(SA.INTEGER)
    content = SA.Column(SA.TEXT)  # max = 21845
    edit = SA.Column(SA.String(1024))
    url = SA.Column(SA.String(1024))

    @classmethod
    def create(cls, session, h1, content, edit, url):
            wiki_first = Wiki_first()
            wiki_first.h1 = h1
            wiki_first.content = content
            wiki_first.edit = edit
            wiki_first.url = url
            session.add(wiki_first)
            session.commit()
            return wiki_first

