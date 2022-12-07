import sqlite3 as sqlite
import uuid
import json
import logging
from be.model import mydb_conn
from be.model import error
from datetime import datetime
from datetime import timedelta
import uuid
import time
import threading
import sqlalchemy

to_be_overtime={}
def overtime_append(key,value):#对to_be_overtime进行操作
    global to_be_overtime
    if key in to_be_overtime:
        to_be_overtime[key].append(value)
    else:
        to_be_overtime[key]=[value]

class TimerClass(threading.Thread):
    def __init__(self):
        threading.Thread.__init__(self)
        self.event = threading.Event()

    def thread(self):
        Buyer().auto_cancel(to_be_overtime[(datetime.utcnow() + timedelta(seconds=1)).second])

    def run(self):  # 每秒运行一次 将超时订单删去
        global to_be_overtime
        while not self.event.is_set():
            self.event.wait(1)
            if (datetime.utcnow() + timedelta(seconds=1)).second in to_be_overtime:
                self.thread()

    def cancel_timer(self):
        self.event.set()

# tmr = TimerClass()# 在无需测试自动取消订单test时删去
# tmr.start()# 在无需测试自动取消订单test时删去

class Buyer(mydb_conn.DBConn):
    def __init__(self):
        mydb_conn.DBConn.__init__(self)
    
    #modified
    def new_order(self, user_id: str, store_id: str, id_and_count: [(str, int)]) -> (int, str, str):
        order_id = ""
        total_price = 0
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id) + (order_id, )
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id) + (order_id, )
            uid = "{}_{}_{}".format(user_id, store_id, str(uuid.uuid1()))

            for book_id, count in id_and_count:
                cursor = self.conn.execute(
                    "SELECT book_id, stock_level, book_info FROM store "
                    "WHERE store_id = '%s' AND book_id = '%s';"%(store_id, book_id))
                row = cursor.fetchone()
                if row is None:
                    return error.error_non_exist_book_id(book_id) + (order_id, )

                stock_level = row[1]
                book_info = row[2]
                book_info_json = json.loads(book_info)
                price = book_info_json.get("price")

                if stock_level < count:
                    return error.error_stock_level_low(book_id) + (order_id,)

                cursor = self.conn.execute(
                    "UPDATE store set stock_level = stock_level - %d "
                    "WHERE store_id = '%s' and book_id = '%s' and stock_level >= %d; "%
                    (count, store_id, book_id, count))
                if cursor.rowcount == 0:
                    # self.conn.rollback()
                    return error.error_stock_level_low(book_id) + (order_id, )

                self.conn.execute(
                        "INSERT INTO new_order_detail(order_id, book_id, count, price) "
                        "VALUES('%s', '%s', %d, %d);"%
                        (uid, book_id, count, price))
                
                total_price += count*price

            timenow = datetime.utcnow()
            self.conn.execute(
                "INSERT INTO new_order_unpaid(order_id, buyer_id,store_id,price,pt) VALUES('%s', '%s','%s',%d,:timenow);" % (
                    uid, user_id, store_id, total_price),{'timenow':timenow})
            self.conn.commit()
            order_id = uid
        except sqlite.Error as e:
            logging.info("528, {}".format(str(e)))
            return 528, "{}".format(str(e)), ""
        except BaseException as e:
            logging.info("530, {}".format(str(e)))
            print(str(e))
            return 530, "{}".format(str(e)), ""

        return 200, "ok", order_id
    
    #modified
    def payment(self, user_id: str, password: str, order_id: str) -> (int, str):
        conn = self.conn
        try:
            cursor = conn.execute("SELECT order_id, buyer_id, store_id, price FROM new_order_unpaid WHERE order_id = '%s'"%(order_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_invalid_order_id(order_id)

            order_id = row[0]
            buyer_id = row[1]
            store_id = row[2]
            total_price =  row[3]

            if buyer_id != user_id:
                return error.error_authorization_fail()

            cursor = conn.execute("SELECT balance, password FROM usr WHERE user_id = '%s';"%(buyer_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_user_id(buyer_id)
            balance = row[0]
            if password != row[1]:
                return error.error_authorization_fail()

            cursor = conn.execute("SELECT store_id, user_id FROM user_store WHERE store_id = '%s';"%(store_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_non_exist_store_id(store_id)

            seller_id = row[1]

            if not self.user_id_exist(seller_id):
                return error.error_non_exist_user_id(seller_id)

            if balance < total_price:
                return error.error_not_sufficient_funds(order_id)
            # buyer -balance
            cursor = conn.execute("UPDATE usr set balance = balance - %d"
                                  "WHERE user_id = '%s' AND balance >= %d"%
                                  (total_price, buyer_id, total_price))
            if cursor.rowcount == 0:
                return error.error_not_sufficient_funds(order_id)
            # seller +balance
            cursor = conn.execute("UPDATE usr set balance = balance + %d"
                                  "WHERE user_id = '%s'"%
                                  (total_price, seller_id))

            cursor = conn.execute("DELETE FROM new_order_unpaid WHERE order_id = '%s'"%(order_id, ))
            if cursor.rowcount == 0:
                return error.error_invalid_order_id(order_id)

            # cursor = conn.execute("DELETE FROM new_order_detail where order_id = '%s'"%(order_id, ))
            # if cursor.rowcount == 0:
            #     return error.error_invalid_order_id(order_id)
            
            timenow = datetime.utcnow()
            conn.execute(
            "INSERT INTO new_order_paid(order_id, buyer_id,store_id,price,status,pt) VALUES('%s', '%s','%s',%d,'%s',:timenow);" % (
                order_id, buyer_id, store_id, total_price, 0),{'timenow':timenow})
            conn.commit()

        except sqlite.Error as e:
            return 528, "{}".format(str(e))

        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def add_funds(self, user_id, password, add_value) -> (int, str):
        try:
            cursor = self.conn.execute("SELECT password  from usr where user_id='%s'"%(user_id,))
            row = cursor.fetchone()
            if row is None:
                return error.error_authorization_fail()

            if row[0] != password:
                return error.error_authorization_fail()

            cursor = self.conn.execute(
                "UPDATE usr SET balance = balance + %d WHERE user_id = '%s'"%
                (add_value, user_id))
            if cursor.rowcount == 0:
                return error.error_non_exist_user_id(user_id)

            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    # ------Search Part------
    def search_global(self, user_id, stype, svalue,page) -> (int,str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if stype not in ['invert_tag', 'invert_title', 'invert_content', 'info']:
                return error.error_not_exist_search_type(stype)
            if stype == 'info': ## later
                cursor = self.conn.execute(
                    " select * from book "
                    " where to_tsvector('english', book_intro) "
                    " @@ to_tsquery('english','%s')"
                    " limit %d offset %d"%(svalue,10,(page-1)*10)
                )
                row = cursor.fetchall()
                return 200, 'ok'
            page = int(page)
            cursor = self.conn.execute("SELECT *  from book as a"
            " inner join (select book_id from %s where keyword = '%s') as b"
            " on a.book_id = b.book_id"
            " limit %d offset %d"%(stype,svalue,10,(page-1)*10))
            row = cursor.fetchall()
            

        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"

    def search_store(self, user_id, stype, svalue, store_id,page) -> (int,str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            
            if stype not in ['invert_tag', 'invert_title', 'invert_content', 'info']:
                return error.error_not_exist_search_type(stype)
            if stype == 'info': ## later
                cursor = self.conn.execute(
                    " select * from book as a inner join (select book_id from store where store_id = '%s') as c "
                    " on a.book_id = c.book_id"
                    " where to_tsvector('english', book_intro) "
                    " @@ to_tsquery('english','%s')"
                    " limit %d offset %d"%(store_id,svalue,10,(page-1)*10)
                )
                row = cursor.fetchall()
                return 200, 'ok'
            page = int(page)
            cursor = self.conn.execute("SELECT *  from book as a"
            " inner join (select book_id from %s where keyword = '%s') as b"
            " on a.book_id = b.book_id"
            " inner join (select book_id from store where store_id = '%s') as c"
            " on a.book_id = c.book_id"
            " limit %d offset %d"%(stype,svalue,store_id,10,(page-1)*10))
            row = cursor.fetchall()
            
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))

        return 200, "ok"
    # 收货
    def receive_book(self, user_id: str, order_id: str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.order_id_exist(order_id):
                return error.error_invalid_order_id(order_id)

            cursor = self.conn.execute("SELECT buyer_id, status FROM new_order_paid WHERE order_id = :order_id",
                                  {"order_id": order_id, })
            row = cursor.fetchone()

            buyer_id = row[0]
            status = row[1]

            if buyer_id != user_id:
                return error.error_authorization_fail()
            if status != 1:
                return error.error_invalid_order_status(order_id)
            
            self.conn.execute(
                "UPDATE new_order_paid set status=2 where order_id = '%s';"%(order_id))
            self.conn.commit()
        
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"


    # 用户订单
    def check_user(self, user_id):
        user = self.conn.execute("SELECT user_id FROM usr WHERE user_id = '%s';" % (user_id,)).fetchone()
        if user is None:
            return False
        else:
            return True
    
    def search_order(self, buyer_id):
        if not self.check_user(buyer_id):
            code, mes = error.error_non_exist_user_id(buyer_id)
            return code, mes, " "
        ret=[]
        #已付款
        records=self.conn.execute(
            " SELECT new_order_detail.order_id,title,new_order_detail.price,count,status,pt,new_order_paid.price "
            "FROM new_order_paid,new_order_detail,book WHERE book.book_id=new_order_detail.book_id and "
            "new_order_paid.order_id=new_order_detail.order_id and new_order_paid.buyer_id = '%s' order by new_order_detail.order_id" % (buyer_id)).fetchall()
        if len(records)!=0:
            #上一条记录的order id
            order_id_previous = records[0][0]
            statusmap = ['未发货', '已发货', '已收货']
            details=[]
            for i in range(len(records)):
                record=records[i]
                #现在的order id
                order_id_current=record[0]
                #同一个订单
                if order_id_current==order_id_previous :
                    details.append({'title':record[1],'price':record[2],'count':record[3]})
                else:
                    status=records[i-1][4]
                    ret.append({'order_id':order_id_previous,'status':statusmap[status],'time':json.dumps(records[i-1][5],cls=DateEncoder),'total_price':records[i-1][6],'detail':details})
                    details = []
                    details.append({'title': record[1], 'price': record[2], 'count': record[3]})
                order_id_previous=order_id_current
            status= records[- 1][4]
            ret.append({'order_id': order_id_previous, 'status': statusmap[status], 'time': json.dumps(records[- 1][5],cls=DateEncoder),'total_price':records[i-1][6],
                        'detail': details})
        # 未付款
        records = self.conn.execute(
            "SELECT new_order_detail.order_id,title,new_order_detail.price,count,pt,new_order_unpaid.price "
            "FROM new_order_unpaid,new_order_detail,book WHERE book.book_id=new_order_detail.book_id and "
            "new_order_unpaid.order_id=new_order_detail.order_id and buyer_id = '%s'" % (buyer_id)).fetchall()
        if len(records)!=0:
            #上一条记录的order id
            order_id_previous = records[0][0]
            details=[]
            for i in range(len(records)):
                record=records[i]
                #现在的order id
                order_id_current=record[0]
                #同一个订单
                if order_id_current==order_id_previous :
                    details.append({'title':record[1],'price':record[2],'count':record[3]})
                else:
                    ret.append({'order_id':order_id_previous,'status':'未付款','time':json.dumps(records[i-1][4],cls=DateEncoder),'total_price':records[i-1][5],'detail':details})
                    details = []
                    details.append({'title': record[1], 'price': record[2], 'count': record[3]})
                order_id_previous=order_id_current
            ret.append({'order_id': order_id_previous, 'status':'未付款', 'time': json.dumps(records[- 1][4],cls=DateEncoder),'total_price':records[i-1][5],
                        'detail': details})
        if len(ret) != 0:
            return 200, 'ok', ret
        else:
            return 200, 'ok', " "

    def cancel(self,buyer_id, order_id):
        if not self.check_user(buyer_id):
            code, mes = error.error_non_exist_user_id(buyer_id)
            return code, mes
        #是否属于未付款订单
        store = self.conn.execute("Select store_id,price FROM new_order_unpaid WHERE order_id = '%s' and buyer_id='%s'" % (order_id,buyer_id)).fetchone()
        if store is not None:
            store_id=store[0]
            price=store[1]
            row = self.conn.execute("DELETE FROM new_order_unpaid WHERE order_id = '%s'" % (order_id,))
        else:
            # 是否属于已付款且未发货订单
            order_info = self.conn.execute(
                "Select store_id,price FROM new_order_paid WHERE order_id = '%s' and buyer_id='%s' and status='0'" % (order_id,buyer_id)).fetchone()
            if order_info is not None:
                store_id = order_info[0]
                price = order_info[1]
                self.conn.execute("DELETE FROM new_order_paid WHERE order_id = '%s' and status='0'" % (order_id,))
                # 卖家减钱
                user_id = self.conn.execute(
                    "SELECT user_id FROM user_store WHERE store_id = '%s';" % (order_info[0],)).fetchone()
                self.conn.execute(
                    "UPDATE usr set balance = balance - %d WHERE user_id = '%s'" % (order_info[1], user_id[0]))
                #买家加钱
                self.conn.execute(
                    "UPDATE usr set balance = balance + %d WHERE user_id = '%s'" % (order_info[1], buyer_id))
            else:
                #无法取消
                return error.error_invalid_order_id(order_id)
        timenow = datetime.utcnow()
        self.conn.execute(
            "INSERT INTO new_order_canceled(order_id, buyer_id,store_id,price,pt) VALUES('%s', '%s','%s',%d,:timenow);" % (
                order_id, buyer_id, store_id, price), {'timenow': timenow})
        #加库存
        self.conn.execute(
                    "Update store Set stock_level = stock_level +  count from new_order_detail Where new_order_detail.book_id = store.book_id and store.store_id = '%s' and new_order_detail.order_id = '%s'" % (store_id,order_id))
        self.conn.commit()
        return 200, 'ok'


    def auto_cancel(self,order_id_list):#自动取消订单
        exist_order_need_cancel=0
        #是否属于未付款订单
        for order_id in order_id_list:
            store = self.conn.execute("Select buyer_id,store_id,price FROM new_order_unpaid WHERE order_id = '%s'" % (order_id)).fetchone()

            if store is not None:
                buyer_id=store[0]
                store_id=store[1]
                price=store[2]
                row = self.conn.execute("DELETE FROM new_order_unpaid WHERE order_id = '%s'" % (order_id,))
                timenow = datetime.utcnow()
                self.conn.execute(
                    "INSERT INTO new_order_canceled(order_id, buyer_id,store_id,price,pt) VALUES('%s', '%s','%s',%d,:timenow);" % (
                        order_id, buyer_id, store_id, price), {'timenow': timenow})
                self.conn.commit()
                exist_order_need_cancel = 1
        return 'no_such_order' if exist_order_need_cancel==0 else "auto_cancel_done"
    
class DateEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.strftime("%Y-%m-%d %H:%M:%S")
        else:
            return json.JSONEncoder.default(self, obj)

