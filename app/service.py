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
import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from werkzeug.exceptions import NotFound,BadRequest
import json
from werkzeug.exceptions import NotFound

from model import Shopcart, DataValidationError

# Import Flask application
from . import app



import sys
import logging
from flask import jsonify, request, json, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
from flask_restplus import Api, Resource, fields
from werkzeug.exceptions import NotFound
from app.model import Shopcart, DataValidationError, DatabaseConnectionError
from . import app

######################################################################
# Configure Swagger before initilaizing it
######################################################################
api = Api(app,
          version='1.0.0',
          title='Shopcarts REST API Service',
          description='This service aims at providing users facility to add, remove, modify and list items in their cart.',
          doc='/apidocs/'
          # prefix='/api'
         )
# This namespace is the start of the path i.e., /pets
ns = api.namespace('shopcarts', description='Shopcart operations')


# Define the model so that the docs reflect what can be sent
shopcart_model = api.model('Shopcart', {
    'user_id': fields.Integer(readOnly=True,
                         description='The unique id of the user'),
    'product_id': fields.Integer(required=True,
                          description='he unique id of the product'),
    'quantity': fields.Integer(required=True,
                              description='The quantity or number of that particular product we want to add to cart'),
    'price': fields.Integer(required=True,
                                description='Cost of one item of the product')
})

######################################################################
# Special Error Handlers
######################################################################

@api.errorhandler(DatabaseConnectionError)
def database_connection_error(error):
    """ Handles Database Errors from connection attempts """
    message = error.message or str(error)
    app.logger.critical(message)
    return {'status':500, 'error': 'Server Error', 'message': message}, 500

@api.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

######################################################################
# GET HEALTH CHECK
######################################################################
@app.route('/healthcheck')
def healthcheck():
    """ Let them know our heart is still beating """
    return make_response(jsonify(status=200, message='Healthy'), status.HTTP_200_OK)


######################################################################
#  PATH: /shopcarts/{user_id}
######################################################################
@ns.route('/<int:user_id>')
@ns.param('user_id','The User Identifier')
class ShopcartResource(Resource):
    """
    ShopcartResource class

    Allows the manipulation of a shopcart of a user
    GET /user{id} - Returns the list of the product in shopcart of a user with that user_id
    DELETE /user{id} - Deletes the list of the product in the shopcart of the user
    """

        
    #################################################################
    # GET THE LIST OF THE PRODUCT IN A USER'S SHOPCART
    #################################################################
    @ns.doc('get_shopcart_list')
    #@ns.response(404, 'Shopcart not found')
    @ns.marshal_list_with(shopcart_model)
    def get(self, user_id):
       """ Get the shopcart entry for user (user_id)
       This endpoint will show the list of products in user's shopcart from the database
       """

       app.logger.info("Request to get the list of the product in a user [%s]'s shopcart", user_id)
       shopcarts = []
       shopcarts = Shopcart.findByUserId(user_id)
       if not shopcarts:
           raise NotFound("Shopcart with user_id '{}' was not found.".format(user_id))
       results = [shopcart.serialize() for shopcart in shopcarts]
       return results, status.HTTP_200_OK

    ######################################################################
    # DELETE ALL PRODUCT OF USER
    ######################################################################
    @ns.doc('delete_user_shopcart')
    @ns.response(204, 'User Shopcart deleted')
    def delete(self, user_id):
       """
       Delete Product of User
       This endpoint will delete all Product of user based the user_id specified in the path
       """

       app.logger.info('Request to delete a shopcart of user id [%s]', user_id)
       shopcarts = Shopcart.findByUserId(user_id)
       if shopcarts:
          for shopcart in shopcarts:
              shopcart.delete()
       return '', status.HTTP_204_NO_CONTENT




######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

@app.before_first_request
def init_db():
    """ Initlaize the model """
    global app
    Shopcart.init_db(app)

# load sample data
def data_load(payload):
    """ Loads a Shopcart entry into the database """
    shopcart = Shopcart(payload['user_id'], payload['product_id'], payload['quantity'], payload['price'])
    shopcart.save()

def data_reset():
    """ Removes all Shopcart data from the database """
    Shopcart.remove_all()

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(status.HTTP_415_UNSUPPORTED_MEDIA_TYPE, 'Content-Type must be {}'.format(content_type))

#@app.before_first_request
def initialize_logging(log_level=logging.INFO):
    """ Initialized the default logging to STDOUT """
    if not app.debug:
        print 'Setting up logging...'
        # Set up default logging for submodules to use STDOUT
        # datefmt='%m/%d/%Y %I:%M:%S %p'
        fmt = '[%(asctime)s] %(levelname)s in %(module)s: %(message)s'
        logging.basicConfig(stream=sys.stdout, level=log_level, format=fmt)
        # Make a new log handler that uses STDOUT
        handler = logging.StreamHandler(sys.stdout)
        handler.setFormatter(logging.Formatter(fmt))
        handler.setLevel(log_level)
        # Remove the Flask default handlers and use our own
        handler_list = list(app.logger.handlers)
        for log_handler in handler_list:
            app.logger.removeHandler(log_handler)
        app.logger.addHandler(handler)
        app.logger.setLevel(log_level)
        app.logger.info('Logging handler established')



