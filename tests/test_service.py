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

    def test_list_shop_cart_entry_by_user_id(self):
        """ Query shopcart by user_id """
        shopcart = Shopcart.findByUserId(1)
        print(shopcart[0].user_id)
        resp = self.app.get('/shopcarts/{}'.format(shopcart[0].user_id),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        #self.assertEqual(len(resp.data), len(shopcart))
        #self.assertEqual(data['user_id'], 1)
        self.assertTrue(len(resp.data) > 0)


    def test_shop_cart_amount_by_user_id(self):
        """ Query the total amount of products in shopcart by user_id"""
        shopcarts = Shopcart.findByUserId(1)
        total = 0.0
        for shopcart in shopcarts:
             total = total + shopcart.price * shopcart.quantity
        total = round(total, 2)
        resp = self.app.get('/shopcarts/1/total',
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        new_json = json.loads(resp.data)
        self.assertEqual(total, new_json['total_price']) 





    def test_update_shopcart_quantity(self):

        """ Update a Shopcart quantity """
        # Add test product in database
        test_product = dict(user_id=1, product_id=1, quantity=5, price=12.00)
        data = json.dumps(test_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # update the test product quantity
        shopcart = Shopcart.find(1, 1)
        resp = self.app.put('/shopcarts/{uid}/product/{pid}'.format(uid = shopcart.user_id, pid = shopcart.product_id),
                            data=data,
                            content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)

        #Check quantity is updated to 3
        new_json = json.loads(resp.data)
        self.assertEqual(new_json['quantity'], 5)


    def test_get_shopcart_product_info(self):
        """ Query quantity and price of a product shopcart by user_id and product_id """
        # Add test product in database
        test_product = dict(user_id=10, product_id=1, quantity=1, price=12.00)
        data = json.dumps(test_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Fetch info of product
        shopcart = Shopcart.find(10, 1)
        resp = self.app.get('/shopcarts/{}/products/{}'.format(shopcart.user_id, shopcart.product_id),
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        ans = json.loads(resp.data)
        self.assertEqual(ans['quantity'], shopcart.quantity)
        self.assertEqual(ans['price'], shopcart.price)

    def test_delete_product(self):
        """ Delete product in Shopcart """
        # Add test product in database
        test_product = dict(user_id=1, product_id=1, quantity=1, price=12.00)
        data = json.dumps(test_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Delet the test product
        shopcart = Shopcart.find(1, 1)
        resp = self.app.delete('/shopcarts/{uid}/product/{pid}'.format(uid = shopcart.user_id, pid = shopcart.product_id))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)

    def test_delete_user_product(self):
        """ Delete products in Shopcart """
        # Add test products in database
        test_product = dict(user_id=1, product_id=1, quantity=1, price=12.00)
        data = json.dumps(test_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        test_product = dict(user_id=1, product_id=3, quantity=1, price=12.00)
        data = json.dumps(test_product)
        resp = self.app.post('/shopcarts',
                             data=data,
                             content_type='application/json')
        self.assertEqual(resp.status_code, status.HTTP_201_CREATED)
        # Delet the test products of same user
        resp = self.app.delete('/shopcarts/{uid}'.format(uid = 1))
        self.assertEqual(resp.status_code, status.HTTP_204_NO_CONTENT)


######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
