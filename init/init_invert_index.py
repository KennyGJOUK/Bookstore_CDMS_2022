import sqlalchemy
from sqlalchemy import Column, String, create_engine, Integer, Text, Date, LargeBinary
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.ext.declarative import declarative_base
import time,sys,os
from sqlalchemy import create_engine
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from be.model import mydb
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fe.access.book import BookDB
import jieba
Base = declarative_base()

class Tags(Base):
    __tablename__ = 'invert_tag'
    id = Column(Integer, primary_key = True)
    keyword = Column(Text, nullable = False, index = True)
    book_id = Column(Text)

class Title(Base):
    __tablename__ = 'invert_title'
    id = Column(Integer, primary_key = True)
    keyword = Column(Text, nullable = False, index = True)
    book_id = Column(Text)


class Content(Base):
    __tablename__ = 'invert_content'
    id = Column(Integer, primary_key = True)
    keyword = Column(Text, nullable = False, index = True)
    book_id = Column(Text)

## create table
def init():
    mydb.init_db()
    tmp = mydb.get_db_conn()
    engine = mydb.get_db_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    tmp.commit()
    tmp.close()

## get data from remote db
def get_data(tmp):
    data = tmp.execute('select * from book;').fetchall()
    return data

## get rid of duplicate and useless symbols
def myfilter(data):
    stop_word = ['', '\n', '、','（','）','，',' ','(',')','.','·']
    data = set(filter(lambda x:x not in stop_word,data))
    return list(data)

## insert tag data into invert index table
def add_tag(tmp,book_id,keyword):
    keyword = keyword.split(',')
    keyword = myfilter(keyword)
    for i in keyword:
        new_tag = Tags(book_id=book_id, keyword=i)
        tmp.add(new_tag)

## insert title data into invert index table
def add_title(tmp,book_id,title):
    title = list(jieba.cut(title, cut_all=True))
    title = myfilter(title)
    for i in title:
        new_title = Title(book_id=book_id, keyword=i)
        tmp.add(new_title)

## insert content data into invert index table
def add_content(tmp,book_id,content):
    content = list(jieba.cut(content, cut_all=True))
    content = myfilter(content)
    for i in content:
        new_content = Content(book_id=book_id, keyword=i)
        tmp.add(new_content)

## build invert index
def build_invert_index():
    tmp = mydb.get_db_conn()
    data = get_data(tmp)
    
    ## iterate the data and insert the related attributes of each row into table
    for i in data:
        book_id = i.book_id
        add_tag(tmp, book_id, i.tags)
        add_content(tmp, book_id, i.content)
        add_title(tmp, book_id, i.title)

    tmp.commit()
    tmp.close()

if __name__ == "__main__":
    init()
    build_invert_index()