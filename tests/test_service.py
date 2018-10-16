# Copyright 2016, 2017 John J. Rofrano. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# https://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""
Shopcart API Service Test Suite

Test cases can be run with the following:
  nosetests -v --with-spec --spec-color
  coverage report -m
  codecov --token=$CODECOV_TOKEN
"""
import unittest
import os
import json
import logging
from flask_api import status    # HTTP Status Codes
from mock import MagicMock, patch

from app.model import Shopcart, DataValidationError, db
import app.service as service

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

######################################################################
#  T E S T   C A S E S
######################################################################
class TestShopcartServer(unittest.TestCase):
    """ Shopcart Server Tests """

    @classmethod
    def setUpClass(cls):
        """ Run once before all tests """
        service.app.debug = False
        service.initialize_logging(logging.INFO)
        # Set up the test database
        service.app.config['SQLALCHEMY_DATABASE_URI'] = DATABASE_URI

    @classmethod
    def tearDownClass(cls):
        pass

    def setUp(self):
        """ Runs before each test """
        service.init_db()
        db.drop_all()    # clean up the last tests
        db.create_all()  # create new tables
        Shopcart(user_id=1, product_id=1, quantity=1, price=12.00).save()
        Shopcart(user_id=1, product_id=2, quantity=1, price=15.00).save()
        self.app = service.app.test_client()

    def tearDown(self):
        db.session.remove()
        db.drop_all()

    def test_create_shopcart_entry_new_product(self):
        """ Create a new Shopcart entry - add new product"""

        # add a new product to shopcart of user
        new_product = dict(user_id=2, product_id=1, quantity=1, price=12.00)
        data = json.dumps(new_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        #Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['user_id'], 2)
        self.assertEqual(new_json['product_id'], 1)

        #Check if you can find the entry in database
        result = Shopcart.find(new_product['user_id'], new_product['product_id'])
        self.assertEqual(new_json['user_id'], result.user_id)
        self.assertEqual(new_json['product_id'], result.product_id)

    def test_create_shopcart_entry_existing_product(self):
        """ Create a new Shopcart entry - add one more item of existing product """

        # add a same type of product to shopcart of user
        new_product = dict(user_id=1, product_id=1, quantity=1, price=12.00)
        data = json.dumps(new_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)

        #Check the data is correct
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['user_id'], 1)
        self.assertEqual(new_json['product_id'], 1)

        #Check if you can find the entry in database with quantity updated by 1
        result = Shopcart.find(new_product['user_id'], new_product['product_id'])
        self.assertEqual(new_json['user_id'], result.user_id)
        self.assertEqual(new_json['product_id'], result.product_id)
        self.assertEqual(new_json['quantity'], 2)



######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
