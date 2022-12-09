import sqlalchemy
from sqlalchemy import Column, String, create_engine, Integer, Text, Date
from sqlalchemy.orm import sessionmaker,scoped_session
from sqlalchemy.ext.declarative import declarative_base
import time
from sqlalchemy import create_engine
class mydb:
    def __init__(self) -> None:
        self.engine = create_engine("postgresql://stu10194810401:Stu10194810401@dase-cdms-2022-pub.pg.rds.aliyuncs.com:5432/stu10194810401",
           
        )

    def get_db_conn(self):
        engine = self.engine
        DbSession = sessionmaker(bind=engine)
        session = DbSession()
        return session
    
    def get_db_engine(self):
        return self.engine


db_obj = None

def init_db():
    global db_obj
    db_obj = mydb()

def get_db_conn():
    global db_obj
    return db_obj.get_db_conn()

def get_db_engine():
    global db_obj
    return db_obj.get_db_engine()