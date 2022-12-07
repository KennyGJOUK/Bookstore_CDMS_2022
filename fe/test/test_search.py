import time

import pytest

from fe.access import auth
from fe import conf
from fe.access.new_buyer import register_new_buyer
from fe.access.new_seller import register_new_seller
import uuid
from fe.test.gen_book_data import GenBook

class TestSearch:
    @pytest.fixture(autouse=True)
    def pre_run_initialization(self):
        self.user_id = "test_search_user_{}".format(str(uuid.uuid1()))
        self.password = "test_search_password_{}".format(str(uuid.uuid1()))
        self.seller_id = "test_search_seller_id_{}".format(str(uuid.uuid1()))
        self.store_id = "test_search_store_id_{}".format(str(uuid.uuid1()))
        
        self.buyer = register_new_buyer(self.user_id, self.password)
        self.seller = register_new_seller(self.seller_id, self.password)
        
        self.stype_list = ['invert_tag', 'invert_content', 'invert_title', 'info']
        self.svalue = "test_search_svalue_{}".format(str(uuid.uuid1()))
        self.page = 1

        code = self.seller.create_store(self.store_id)
        assert code == 200

        yield

    def test_global_ok(self):
        for stype in self.stype_list:
            code = self.buyer.search_global(stype, self.svalue, self.page)
            assert code == 200

    def test_non_exist_stype_global(self):
        stype = "tags_non_exist"
        code = self.buyer.search_global(stype, self.svalue,
         self.page)
        assert code != 200

    def test_non_exist_stype_store(self):
        stype = "tags_non_exist"
        code = self.buyer.search_store(stype, self.svalue,
         self.page, self.store_id)
        assert code != 200

    def test_store_ok(self):
        for stype in self.stype_list:
            code = self.buyer.search_store(stype, self.svalue,
             self.page, self.store_id)
            assert code == 200

    def test_non_exist_store_id(self):
        store_id = self.store_id + "_non_exist"
        stype = self.stype_list[0]
        code = self.buyer.search_store(stype, self.svalue, self.page, store_id)
        assert code != 200

    def test_non_exist_user_id_global(self):
        self.buyer.user_id = self.buyer.user_id + '_non_exist'
        stype = self.stype_list[0]
        code = self.buyer.search_global(stype, self.svalue, self.page)
        assert code != 200

    def test_non_exist_user_id_store(self):
        self.buyer.user_id = self.buyer.user_id + '_non_exist'
        stype = self.stype_list[0]
        code = self.buyer.search_store(stype, self.svalue, self.page, self.store_id)
        assert code != 200

    

    

    
