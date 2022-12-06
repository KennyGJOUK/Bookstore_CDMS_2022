from be.model import mydb


class DBConn:
    def __init__(self):
        self.conn = mydb.get_db_conn()

    def user_id_exist(self, user_id):
        cursor = self.conn.execute("SELECT user_id FROM usr WHERE user_id = '%s';"%(user_id,))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def book_id_exist(self, store_id, book_id):
        cursor = self.conn.execute("SELECT book_id FROM store WHERE store_id = '%s' AND book_id = '%s';"%(store_id, book_id))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True

    def store_id_exist(self, store_id):
        cursor = self.conn.execute("SELECT store_id FROM user_store WHERE store_id = '%s';"%(store_id,))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True
 
    def order_id_exist(self, order_id):
        cursor = self.conn.execute("SELECT order_id FROM new_order_paid WHERE order_id = '%s';"%(order_id,))
        row = cursor.fetchone()
        if row is None:
            return False
        else:
            return True
    
    def store_id_match_user_id(self, user_id, store_id):
        cursor = self.conn.execute("SELECT user_id FROM user_store WHERE store_id = '%s';"%(store_id,))
        row = cursor.fetchone()
        if (row[0]  == user_id):
            return True
        else:
            return False
