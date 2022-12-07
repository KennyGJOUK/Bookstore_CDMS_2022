import sqlite3 as sqlite
from be.model import error
from be.model import mydb_conn
from sqlalchemy.exc import SQLAlchemyError

class Seller(mydb_conn.DBConn):

    def __init__(self):
        mydb_conn.DBConn.__init__(self)

    def add_book(self, user_id: str, store_id: str, book_id: str, book_json_str: str, stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if self.book_id_exist(store_id, book_id):
                return error.error_exist_book_id(book_id)

            self.conn.execute("INSERT into store(store_id, book_id, book_info, stock_level)"
                              "VALUES ('%s', '%s', '%s', %d)"%(store_id, book_id, book_json_str, stock_level))
            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def add_stock_level(self, user_id: str, store_id: str, book_id: str, add_stock_level: int):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.book_id_exist(store_id, book_id):
                return error.error_non_exist_book_id(book_id)

            self.conn.execute("UPDATE store SET stock_level = stock_level + %d "
                              "WHERE store_id = '%s' AND book_id = '%s'"%(add_stock_level, store_id, book_id))
            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"

    def create_store(self, user_id: str, store_id: str) -> (int, str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if self.store_id_exist(store_id):
                return error.error_exist_store_id(store_id)
            self.conn.execute("INSERT into user_store(store_id, user_id)"
                              "VALUES ('%s', '%s')"%(store_id, user_id))
            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            print(str(e))
            return 530, "{}".format(str(e))
        return 200, "ok"

    # 发货
    def deliver_book(self, user_id: str, store_id: str, order_id: str):
        try:
            if not self.user_id_exist(user_id):
                return error.error_non_exist_user_id(user_id)
            if not self.store_id_exist(store_id):
                return error.error_non_exist_store_id(store_id)
            if not self.store_id_match_user_id(user_id, store_id): # add store_id_match_user_id() in mydb_conn.py
                return error.error_authorization_fail()
            if not self.order_id_exist(order_id): # add order_id_exist() in mydb_conn.py
                return error.error_invalid_order_id(order_id)
            
            cursor = self.conn.execute(
                "SELECT status FROM new_order_paid where order_id = '%s';"%(order_id))
            row = cursor.fetchone()
            status  = row[0]
            # order_status 非待发货
            if status != 0:
                # add error_invalid_order_status in error.py
                return error.error_invalid_order_status(order_id)
            # update order_status 
            self.conn.execute(
                "UPDATE new_order_paid set status=1 where order_id = '%s';"%(order_id))
            self.conn.commit()
        except sqlite.Error as e:
            return 528, "{}".format(str(e))
        except BaseException as e:
            return 530, "{}".format(str(e))
        return 200, "ok"