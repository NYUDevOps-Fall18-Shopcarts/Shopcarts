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


######################################################################
# Error Handlers
######################################################################
@app.errorhandler(DataValidationError)
def request_validation_error(error):
    """ Handles Value Errors from bad data """
    return bad_request(error)

@app.errorhandler(400)
def bad_request(error):
    """ Handles bad reuests with 400_BAD_REQUEST """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=400, error='Bad Request', message=message), 400

@app.errorhandler(404)
def not_found(error):
    """ Handles resources not found with 404_NOT_FOUND """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=404, error='Not Found', message=message), 404

@app.errorhandler(405)
def method_not_supported(error):
    """ Handles unsuppoted HTTP methods with 405_METHOD_NOT_SUPPORTED """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=405, error='Method not Allowed', message=message), 405

@app.errorhandler(415)
def mediatype_not_supported(error):
    """ Handles unsuppoted media requests with 415_UNSUPPORTED_MEDIA_TYPE """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=415, error='Unsupported media type', message=message), 415

@app.errorhandler(500)
def internal_server_error(error):
    """ Handles unexpected server error with 500_SERVER_ERROR """
    message = error.message or str(error)
    app.logger.info(message)
    return jsonify(status=500, error='Internal Server Error', message=message), 500


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    # return jsonify(name='Shopcarts REST API Service',
    #                version='1.0',
    #                description='This service aims at providing users facility to add, remove, modify and list items in their cart.'),\
    #                status.HTTP_200_OK
    return app.send_static_file('index.html')

######################################################################
# ADD A NEW PRODUCT TO USER'S SHOPCART
######################################################################
@app.route('/shopcarts', methods=['POST'])
def create_shopcart():
    """
    Create a Shopcart entry specific to that user_id and product_id
    This endpoint will create a shopcart based the data in the body that is posted
    """

    check_content_type('application/json')

    shopcart = Shopcart()
    shopcart.deserialize(request.get_json())

    #Check if the entry exists, if yes then increase quantity of product
    exists = Shopcart.find(shopcart.user_id, shopcart.product_id)
    if exists:
        exists.quantity = exists.quantity + 1
        exists.save()
        shopcart = exists

    shopcart.save()
    message = shopcart.serialize()
    location_url = url_for('get_shopcart_product_info', user_id=shopcart.user_id, product_id=shopcart.product_id ,_external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED,
                         {
                             'Location': location_url
                         })

#################################################################
# LIST ALL SHOPCARTS
#################################################################
@app.route('/shopcarts', methods=['GET'])
def list_shopcarts():
    """ Returns all of the Shopcarts """
    shopcarts = []
    product_id = request.args.get('product_id')
    if product_id:
        shopcarts = Shopcart.findByProductId(product_id)
    else:
        shopcarts = Shopcart.all()

    results = [shopcart.serialize() for shopcart in shopcarts]
    return make_response(jsonify(results), status.HTTP_200_OK)

#################################################################
# LIST ALL SHOPCARTS
#################################################################
@app.route('/shopcarts', methods=['GET'])
def list_shopcarts():
    """ Returns all of the Shopcarts """
    shopcarts = []
    product_id = request.args.get('product_id')
    if product_id:
        shopcarts = Shopcart.findByProductId(product_id)
    else:
        shopcarts = Shopcart.all()

    results = [shopcart.serialize() for shopcart in shopcarts]
    return make_response(jsonify(results), status.HTTP_200_OK)

#################################################################
# GET THE LIST OF THE PRODUCT IN A USER'S SHOPCART
#################################################################
@app.route('/shopcarts/<int:user_id>', methods=['GET'])
def get_shopcart(user_id):
    """ Get the shopcart entry for user (user_id)
     This endpoint will show the list of products in user's shopcart from the database
     """
    shopcarts = Shopcart.findByUserId(user_id)
    results = [shopcart.serialize() for shopcart in shopcarts]
    #    abort(status.HTTP_404_NOT_FOUND, "Shopcart with id '{}' was not found.".format(user_id))
    return make_response(jsonify(results), status.HTTP_200_OK)


##################################################################
# GET THE TOTAL AMOUNT OF ALL THE PRODUCTS IN SHOPCART
##################################################################
@app.route('/shopcarts/<int:user_id>/total', methods=['GET'])
def get_shopcart_total(user_id):
    """ Get the total amount of the user's shopcart for user(user_id)
    """
    total_amount = 0.0
    shopcarts = Shopcart.findByUserId(user_id)
    for shopcart in shopcarts:
        total_amount = total_amount + (shopcart.price * shopcart.quantity)
    total_amount = round(total_amount, 2)

    inlist = [shopcart.serialize() for shopcart in shopcarts]

    dt = {'products':inlist,
              'total_price':total_amount}

    results = json.dumps(dt)
    return make_response(results, status.HTTP_200_OK)


######################################################################
# UPDATE AN EXISTING PRODUCT COUNT IN SHOPCART
######################################################################
@app.route('/shopcarts/<int:user_id>/product/<int:product_id>', methods=['PUT'])
def update_shopcart(user_id,product_id):
	"""
	Update a Shopcart entry specific to that user_id and product_id
	This endpoint will update a Shopcart based the data in the body that is posted
	"""
	check_content_type('application/json')
	shopcart = Shopcart.find(user_id, product_id)
	if not shopcart:
		raise NotFound("User with id '{uid}' doesn't have product with id '{pid}' was not found.' in the shopcart ".format(uid = user_id, pid = product_id))
	shopcart.deserialize(request.get_json())
	shopcart.save()
	return make_response(jsonify(shopcart.serialize()), status.HTTP_200_OK)

######################################################################
# READ THE INFORMATION OF AN EXISTING PRODUCT IN SHOPCART
######################################################################
@app.route('/shopcarts/<int:user_id>/product/<int:product_id>', methods=['GET'])
def get_shopcart_product_info(user_id, product_id):
    """Read the information of an exsiting product (product_id) in shopcart of user (user_id)
     This endpoint will show the information of the specified product in user's shopcart from the database
    """
    result = Shopcart.find(user_id, product_id)
    if not result:
        raise NotFound("User with id '{uid}' doesn't have product with id '{pid}' was not found.' in the shopcart ".format(uid = user_id, pid = product_id))
    return make_response(jsonify(result.serialize()),status.HTTP_200_OK)

######################################################################
# DELETE A PRODUCT
######################################################################
@app.route('/shopcarts/<int:user_id>/product/<int:product_id>', methods=['DELETE'])
def delete_products(user_id, product_id):
    """
    Delete a Product
    This endpoint will delete a Product based the id specified in the path
    """
    shopcart = Shopcart.find(user_id, product_id)
    if shopcart:
        shopcart.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)


############################################################################
# QUERY DATABASE FOR SHOPCARTS HAVING PRODUCTS WORTH MORE THAN GIVEN AMOUNT
###########################################################################
@app.route('/shopcarts/users', methods=['GET'])
def get_users_by_total_cost_of_shopcart():
    amount = request.args.get('amount');
    app.logger.info(type(amount))
    if amount is None:
        raise NotFound("Required parameter amount not found")
    else :
        try:
            amount = float(amount)
        except ValueError:
            raise BadRequest("Required parameter 'amount' should be a float")
    result = Shopcart.find_users_by_shopcart_amount(amount);
    return make_response(jsonify(result), status.HTTP_200_OK)


######################################################################
# DELETE ALL PRODUCT OF USER
######################################################################
@app.route('/shopcarts/<int:user_id>', methods=['DELETE'])
def delete_user_products(user_id):
    """
    Delete Product of User
    This endpoint will delete all Product of user based the user_id specified in the path
    """
    shopcarts = Shopcart.findByUserId(user_id)
    if shopcarts:
        for shopcart in shopcarts:
            shopcart.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
# DELETE ALL SHOPCARTS DATA (for testing only)
######################################################################
@app.route('/shopcarts/reset', methods=['DELETE'])
def shopcarts_reset():
    """ Clears all items from shopcarts for all users from the database """
    Shopcart.remove_all()
    return make_response('', status.HTTP_204_NO_CONTENT)

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

@app.before_first_request
def init_db():
    """ Initialies the SQLAlchemy app """
    global app
    Shopcart.init_db(app)

def check_content_type(content_type):
    """ Checks that the media type is correct """
    if request.headers['Content-Type'] == content_type:
        return
    app.logger.error('Invalid Content-Type: %s', request.headers['Content-Type'])
    abort(415, 'Content-Type must be {}'.format(content_type))

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
