
import sqlalchemy
from sqlalchemy import Column, String, create_engine, Integer, Text, Date, LargeBinary, Index
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.ext.declarative import declarative_base
import time,sys,os
from sqlalchemy import create_engine
from be.model import mydb
from sqlalchemy.sql import func
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from fe.access.book import BookDB
Base = declarative_base()


class Book(Base):
    __tablename__ = 'book'
    book_id = Column(Text, primary_key=True)
    title = Column(Text, nullable=False)
    author = Column(Text)
    publisher = Column(Text)
    original_title = Column(Text)
    translator = Column(Text)
    pub_year = Column(Text)
    pages = Column(Integer)
    original_price = Column(Integer)
    binding = Column(Text)
    isbn = Column(Text)
    author_intro = Column(Text)
    book_intro = Column(Text)
    content = Column(Text)
    tags = Column(Text)
    pictures = Column(LargeBinary)

    __table_args__ = (
        Index(
            'ix_content',
            func.to_tsvector('english', book_intro),
            postgresql_using = "gin"
        ),
    )

class Tags(Base):
    __tablename__ = 'invert_tag'
    keyword = Column(Text, nullable = False, primary_key = True)
    book_id = Column(Text)

class Title(Base):
    __tablename__ = 'invert_title'
    keyword = Column(Text, nullable = False, primary_key = True)
    book_id = Column(Text)



def init():
    mydb.init_db()
    tmp = mydb.get_db_conn()
    engine = mydb.get_db_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    tmp.commit()
    tmp.close()

def format_d(s_, s_data):
    s_data_ret = []
    # print(s_data)
    s_data = list(s_data)
    for i in s_data:
        tmp = {}
        for j in s_:
            if j == 'tags':
                tmp[j] = ','.join(i.tags)
            elif j == 'pictures':
                tmp[j] = (''.join(i.pictures)).encode('utf-8')
            elif j == 'id':
                tmp['book_id'] =  eval('i.'+j)
            else:
                tmp[j] =  eval('i.'+j)
        s_data_ret.append(tmp)
        
    return s_data_ret

def add_data():
    db = BookDB()
    ## get total size
    size = db.get_book_count()
    ## get local book data from sqlite
    data = db.get_book_info(0, size)
    mydb.init_db()
    tmp = mydb.get_db_conn()

    ## insert data from sqlite to remote database
    s_ =  ['id','title', 'author', 'publisher', 'original_title', 'translator',
     'pub_year', 'pages', 'price', 'binding', 'isbn',
     'author_intro', 'book_intro', 'content', 'tags', 'pictures']
    tmp.bulk_insert_mappings(Book, format_d(s_, data))
    tmp.commit()
    tmp.close()

if __name__ == "__main__":
    init()
    add_data()