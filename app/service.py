<<<<<<< HEAD
"""
Shopcarts Service
Paths:
------
GET /shopcarts/{id} -Returns list of products in user's shopcart from the database

POST /Shopcarts- Create a Shopcart entry specific to that user_id and product_id

DELETE /shopcarts/{id} - deletes a product record in the database
"""



import sys
import logging
from flask import Flask, jsonify, request, url_for, make_response, abort
from flask_api import status    # HTTP Status Codes
=======
>>>>>>> 75cf7c76d4e43b5f6c41fe61c79c9a5b99e12407



######################################################################
# DELETE A PRODUCT
######################################################################
@app.route('/shopcarts/<int:product_id>', methods=['DELETE'])
def delete_products(product_id):
    """
    Delete a Product
    This endpoint will delete a Product based the id specified in the path
    """
    exists = Shopcart.find(user_id,product_id)
    if exists:
        exists.delete()
    return make_response('', status.HTTP_204_NO_CONTENT)
