import sqlalchemy
from sqlalchemy import Column, String, create_engine, Integer, Text, Date
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.ext.declarative import declarative_base
import time
from sqlalchemy import create_engine
from model import mydb


# engine = create_engine("postgresql://stu10194810401:Stu10194810401@dase-cdms-2022-pub.pg.rds.aliyuncs.com:5432/stu10194810401",
#     max_overflow=0,
#     # 链接池大小
#     pool_size=5,
#     # 链接池中没有可用链接则最多等待的秒数，超过该秒数后报错
#     pool_timeout=10,
#     # 多久之后对链接池中的链接进行一次回收
#     pool_recycle=1,
#     # 查看原生语句（未格式化）
#     echo=True
# )

Base = declarative_base()
# DbSession = sessionmaker(bind=engine)
# session = DbSession()

class User(Base):
    __tablename__ = "usr"
    user_id = Column(Text, primary_key = True)
    password = Column(Text, nullable = False)
    balance = Column(Integer, nullable = False)
    token = Column(Text)
    terminal = Column(Text)

class UserStore(Base):
    __tablename__ = "user_store"
    user_id = Column(Text, primary_key = True)
    store_id = Column(Text, primary_key = True)

class Store(Base):
    __tablename__ = "store"
    store_id = Column(Text, primary_key = True)
    book_id = Column(Text, primary_key = True)
    book_info = Column(Text)
    stock_level = Column(Integer)

class NewOrder(Base):
    __tablename__ = "new_order"
    order_id = Column(Text, primary_key = True)
    user_id = Column(Text)
    store_id = Column(Text)

class NewOrderDetail(Base):
    __tablename__ = "new_order_detail"
    order_id = Column(Text, primary_key = True)
    book_id = Column(Text, primary_key = True)
    count = Column(Integer)
    price = Column(Integer)

def init():
    mydb.init_db()
    tmp = mydb.get_db_conn()
    engine = mydb.get_db_engine()
    Base.metadata.drop_all(engine)
    Base.metadata.create_all(engine)
    tmp.commit()
    tmp.close()

def add_info():
    # engine = mydb.get_db_engine()
    # DBSession = sessionmaker(bind=engine)
    session = mydb.get_db_conn()
    # 提交即保存到数据库A
    A = User(user_id = '王掌柜',
            password = '123456',
            balance = 100,
            token = '***',
            terminal = 'Edge')
    B = User(user_id = '小明',
            password = '123456',
            balance = 500,
            token = '***',
            terminal='Chrome')
    session.add_all([A, B])
    session.commit()

    A_Store1 = UserStore(user_id = '王掌柜',
                        store_id = '王掌柜的书店')
    A_Store2 = UserStore(user_id = '王掌柜',
                        store_id = '王掌柜的进口书店')
    # Book1 = Book(book_id = 0,
    #             title='数据结构')
    # Book2 = Book(book_id=1,
    #             title='PRML')
    # session.add_all([A_Store1, A_Store2, Book1, Book2])
    session.add_all([A_Store1, A_Store2])
    session.commit()

    StoreA = Store(store_id = '王掌柜的书店',
                    book_id = 1,
                    stock_level=10,
                    ) # 价格单位是分
    StoreB = Store(store_id = '王掌柜的进口书店',
                    book_id = 2,
                    stock_level=10,
                    )
    session.add_all([StoreA, StoreB])
    session.commit()
    
    OrderA = NewOrder(order_id = 'order1',
                            user_id = '小明',
                            store_id = '王掌柜的书店',
                            )
    Order_detailA = NewOrderDetail(order_id = 'order1',
                                    book_id = 1,
                                    count = 2,
                                    price = 2000)
    OrderB = NewOrder(order_id = 'order2',
                            user_id = '小明',
                            store_id = '王掌柜的进口书店',
                            )
    Order_detailB = NewOrderDetail(order_id = 'order2',
                                    book_id = 2,
                                    count = 1,
                                    price = 10000)
    session.add_all([OrderA, Order_detailA, OrderB, Order_detailB])
    session.commit()
    # 关闭session
    session.close()

if __name__ == '__main__':
    init()
    add_info()