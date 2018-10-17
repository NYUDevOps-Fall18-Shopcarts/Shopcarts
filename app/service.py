


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
