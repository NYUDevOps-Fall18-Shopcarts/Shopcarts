"""
Shopcart Service with Swagger

Paths:
------
GET / - Displays a UI for Selenium testing
GET /shopcarts - Returns a list of shopcarts belonging to all users
GET /shopcarts/{user_id} - Returns ta shopcarts of specified user_id
POST /shopcarts - adds a new item to shopcart
PUT /shopcarts/{user_id} - updates a product in shopcart of specified user
DELETE /shopcarts/{user_id} - deletes all products in user's shopcart
DELETE /shopcarts/{user_id}/products/{id} - deletes specified product from given user's shopcarts
"""

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

shopcart_collection_model = ('Shopcart Collection', {
    'user_id': fields.(readOnly=True,
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
# GET INDEX
######################################################################
@app.route('/', methods=['GET'])
def index():
    """ Send back a greeting """
    return app.send_static_file('index.html')

######################################################################
#  PATH: /shopcarts/{id}
######################################################################
@ns.route('/<int:user_id>')
@ns.param('user_id', 'The Pet identifier')
class ShopcartResource(Resource):
    """
    PetResource class

    Allows the manipulation of a Shopcart
    GET /user{id} - Retrieves all products in cart of user
    DELETE /user{id} -  Deletes a Pet with the id
    """
    #------------------------------------------------------------------
    # RETRIEVES SHOPCART CONTENTS OF USER
    #------------------------------------------------------------------
    @ns.doc('get_shopcarts')
    @ns.marshal_list_with(shopcart_model)
    def get(self, user_id):
        """
        Retrieve entire shopcart contents of user

        This endpoint will return a list of Shopcart Model where user_id is given user_id
        """
        app.logger.info("Request to Retrieve a shopcart of user with id [%s]", user_id)

        shopcarts = Shopcart.findByUserId(user_id)
        results = [shopcart.serialize() for shopcart in shopcarts]
        return results, status.HTTP_200_OK

    #------------------------------------------------------------------
    # DELETE SHOPCART CONTENTS OF USER
    #------------------------------------------------------------------
    @ns.doc('delete_shopcarts')
    @ns.response(204, 'Shopcart deleted')
    def delete(self, user_id):
        """
        Delete a Shopcart

        This endpoint will delete all products in user's shopcart
        """
        app.logger.info('Request to Delete shopcart contents of user with id [%s]', user_id)
        shopcarts = Shopcart.findByUserId(user_id)
        if shopcarts:
            for shopcart in shopcarts:
                shopcart.delete()

        return '', status.HTTP_204_NO_CONTENT



    

######################################################################
#  PATH: /shopcarts
######################################################################
@ns.route('/', strict_slashes=False)
class PetCollection(Resource):
    """ Handles all interactions with collections of Shopcarts """
    #------------------------------------------------------------------
    # LIST ALL SHOCARTS
    #------------------------------------------------------------------
    @ns.doc('list_shopcarts')
    @ns.param('category', 'List all Shopcarts of all users by category')
    @ns.marshal_list_with(pet_model)
    def get(self):
        """ Returns all of the Pets """
        app.logger.info('Request to list Pets...')
        pets = []
        category = request.args.get('category')
        if category:
            pets = Pet.find_by_category(category)
        else:
            pets = Pet.all()

        app.logger.info('[%s] Pets returned', len(pets))
        results = [pet.serialize() for pet in pets]
        return results, status.HTTP_200_OK
