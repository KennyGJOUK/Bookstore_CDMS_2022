import sqlalchemy
from sqlalchemy import Column, String, create_engine, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.ext.declarative import declarative_base
import time
from sqlalchemy import create_engine
from model import mydb
from datetime import datetime,time

Base = declarative_base()

class User(Base):
    __tablename__ = "usr"
    user_id = Column(Text, primary_key = True)
    password = Column(Text, nullable = False)
    balance = Column(Integer, nullable = False)
    token = Column(Text)
    terminal = Column(Text)

# add unique constraint
class UserStore(Base):
    __tablename__ = "user_store"
    user_id = Column(Text, primary_key = True)
    store_id = Column(Text, primary_key = True, unique = True)

class Store(Base):
    __tablename__ = "store"
    store_id = Column(Text, primary_key = True)
    book_id = Column(Text, primary_key = True)
    book_info = Column(Text)
    stock_level = Column(Integer)

# 未付款订单
class NewOrderUnpaid(Base):
    __tablename__ = 'new_order_unpaid'
    order_id = Column(Text, primary_key=True)
    buyer_id = Column(Text, ForeignKey('usr.user_id'), nullable=False)
    store_id = Column(Text, ForeignKey('user_store.store_id'), nullable=False)
    price = Column(Integer, nullable=False)
    pt = Column(DateTime, nullable=False)


# 已取消订单
class NewOrderCanceled(Base):
    __tablename__ = 'new_order_canceled'
    order_id = Column(Text, primary_key=True)
    buyer_id = Column(Text, ForeignKey('usr.user_id'), nullable=False)
    store_id = Column(Text, ForeignKey('user_store.store_id'), nullable=False)
    price = Column(Integer, nullable=False)
    pt = Column(DateTime, nullable=False)


# 已付款订单
class NewOrderPaid(Base):
    __tablename__ = 'new_order_paid'
    order_id = Column(Text, primary_key=True)
    buyer_id = Column(Text, ForeignKey('usr.user_id'), nullable=False)
    store_id = Column(Text, ForeignKey('user_store.store_id'), nullable=False)
    price = Column(Integer, nullable=False)
    pt = Column(DateTime, nullable=False)
    status = Column(Integer, nullable=False)  # 0为待发货，1为已发货，2为已收货

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
    
    OrderA = NewOrderPaid(order_id = 'order1',
                            buyer_id = '小明',
                            store_id = '王掌柜的书店',
                            price=2000,
                            pt = datetime.now(),
                            status = 0)  # 0为已付款，1为已发货，2为已收货
    Order_detailA = NewOrderDetail(order_id = 'order1',
                                    book_id = 1,
                                    count = 2,
                                    price = 2000)
    OrderB = NewOrderPaid(order_id = 'order2',
                            buyer_id = '小明',
                            store_id = '王掌柜的进口书店',
                            price = 10000,
                            pt = datetime.now(),
                            status = 2)
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