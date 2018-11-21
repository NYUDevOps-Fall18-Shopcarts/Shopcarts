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
from werkzeug.exceptions import NotFound,BadRequest
from app.model import Shopcart, DataValidationError, db
import app.service as service

DATABASE_URI = os.getenv('DATABASE_URI', 'sqlite:///../db/test.db')

# Status Codes
HTTP_200_OK = 200
HTTP_201_CREATED = 201
HTTP_204_NO_CONTENT = 204
HTTP_400_BAD_REQUEST = 400
HTTP_404_NOT_FOUND = 404
HTTP_405_METHOD_NOT_ALLOWED = 405
HTTP_409_CONFLICT = 409
HTTP_415_UNSUPPORTED_MEDIA_TYPE = 415

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
        self.app = service.app.test_client()
        service.initialize_logging(logging.CRITICAL)
        service.init_db()
        service.data_reset()
        service.data_load({"user_id": 1, "product_id": 1, "quantity": 1, "price":12.00})
        service.data_load({"user_id": 1, "product_id": 2, "quantity": 1, "price":15.00})

    def tearDown(self):
        db.session.remove()
        db.drop_all()


    #Needs to be refactored once get method is up
    def test_create_shopcart_entry_new_product(self):
        """ Create a new Shopcart entry - add new product"""

        #Get number of products in users shopcart
        #product_count = self.get_product_count(2)

        product_count = self.get_product_count(2)
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

        # check that count has gone up and includes sammy
        resp = self.app.get('/shopcarts/2/product/1')

        # print 'resp_data(2): ' + resp.data
        data = json.loads(resp.data)
        print(data)
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        self.assertEqual(new_json, data)
        #self.assertEqual(len(data), product_count + 1)

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
# Utility functions
######################################################################

    def get_product_count(self, user_id):
        """ save the current number of products in user's shopcart """
        resp = self.app.get('/shopcarts/'+str(user_id))
        self.assertEqual(resp.status_code, status.HTTP_200_OK)
        data = json.loads(resp.data)
        return len(data)

######################################################################
#   M A I N
######################################################################
if __name__ == '__main__':
    unittest.main()
