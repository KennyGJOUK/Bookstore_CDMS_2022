import uuid
import pytest
from fe.test.gen_book_data import GenBook
from fe.access.new_buyer import register_new_buyer
from fe.access.book import Book

class Testreceivebook:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.store_id = "test_receive_book_store_{}".format(str(uuid.uuid1()))
        self.seller_id = "test_receive_book_seller_{}".format(str(uuid.uuid1()))
        self.store_id = "test_receive_book_store_id_{}".format(str(uuid.uuid1()))
        self.buyer_id = "test_receive_book_buyer_{}".format(str(uuid.uuid1()))
        self.buyer_password = self.buyer_id
        self.buyer = register_new_buyer(self.buyer_id, self.buyer_password)

        gen_book = GenBook(self.seller_id, self.store_id)
        self.seller = gen_book.seller
        ok, buy_book_id_list = gen_book.gen(non_exist_book_id=False, low_stock_level=False, max_book_count=10)
        self.buy_book_info_list = gen_book.buy_book_info_list
        assert ok
        
        code = self.buyer.add_funds(99999999)
        assert code == 200

        code, self.order_id = self.buyer.new_order(self.store_id, buy_book_id_list)
        assert code == 200
        
        code = self.buyer.payment(self.order_id)
        assert code == 200

        code = self.seller.deliver_book(self.seller_id, self.store_id, self.order_id)
        assert code == 200
        yield

    def test_ok(self):
        code = self.buyer.receive_book(self.buyer_id, self.order_id)
        assert code == 200

    def test_error_non_exist_user_id(self):
        code = self.buyer.receive_book("wrong_buyer_id", self.order_id)
        assert code == 511

    def test_error_invalid_order_id(self):
        code = self.buyer.receive_book(self.buyer_id, "wrong_order_id")
        assert code == 518

    def test_repeat_receive_books(self):
        code = self.buyer.receive_book(self.buyer_id, self.order_id)
        assert code == 200
        code = self.buyer.receive_book(self.buyer_id, self.order_id)
        assert code == 520