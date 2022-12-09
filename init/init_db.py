import sqlalchemy
from sqlalchemy import Column, String, create_engine, Integer, Text, DateTime, ForeignKey
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.ext.declarative import declarative_base
import time
from sqlalchemy import create_engine
import sys,os
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))


from be.model import mydb
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
    book_id = Column(Text)
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


if __name__ == '__main__':
    init()
    # add_info()