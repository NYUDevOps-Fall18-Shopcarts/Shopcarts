import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes


from model import Shopcart

# Import Flask application
from . import app


######################################################################
# GET INDEX
######################################################################
@app.route('/')
def index():
    """ Root URL response """
    return jsonify(name='Shopcarts REST API Service',
                   version='1.0',
                   description='This service aims at providing users facility to add, remove, modify and list items in their cart.'),\
                   status.HTTP_200_OK

######################################################################
# ADD A NEW PRODUCT TO USER'S SHOPCART
######################################################################
@app.route('/shopcarts', methods=['POST'])
def create_pets():
    """
    Create a Shopcart entry specific to that user_id and product_id
    This endpoint will create a Pet based the data in the body that is posted
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
    #location_url = url_for('get_pets', pet_id=pet.id, _external=True)
    return make_response(jsonify(message), status.HTTP_201_CREATED)


@app.route('/shopcarts/<int:user_id>', methods=['GET'])
def get_shopcart(user_id):
    """ Get the shopcart entry for user (user_id)
     This endpoint will show the list of products in user's shopcart from the database
     """
    shopcarts = Shopcart.findByUserId(user_id)
    results = [shopcart.serialize() for shopcart in shopcarts]
    #    abort(status.HTTP_404_NOT_FOUND, "Shopcart with id '{}' was not found.".format(user_id))
    return jsonify(name='Shopcarts REST API Service',
                   version='1.0',
                   description='List of products in Shopcarts of user ',
                   data=results),\
                   status.HTTP_200_OK

@app.route('/shopcarts/<int:user_id>/product-amount/<int:product_id>', methods=['GET'])
def get_shopcart_product_amount(user_id, product_id):
    """Get the amount of product (product_id) in shopcart of user (user_id)
     This endpoint will show the amount of the specified product in user's shopcart from the database
    """
    result = Shopcart.find(user_id, product_id).serialize()
    return jsonify(name='Shopcarts REST API Service',
                   version='1.0',
                   description='amount of a product in Shopcarts of a user ',
                   data=result),\
                   status.HTTP_200_OK

######################################################################
#  U T I L I T Y   F U N C T I O N S
######################################################################

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
