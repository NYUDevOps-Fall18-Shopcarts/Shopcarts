"""
Models for Pet Demo Service

All of the models are stored in this module

Models
------
Shopcart - A Shopcart used by each User

Attributes:
-----------
product_id (int)    - the product-id of a Product used to uniquely identify it
user_id (int)       - the user-id of the User which uniquely identifies the User
quantity (int)     - number of items User wants to buy of that particular product
price(float)       - cost of one item of the Product

"""
import logging
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class DataValidationError(Exception):
    """ Used for an data validation errors when deserializing """
    pass

class Shopcart(db.Model):
    """
    Class that represents a Shopcart

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    logger = logging.getLogger(__name__)
    app = None

    # Table Schema
    user_id = db.Column(db.Integer,primary_key=True)
    product_id = db.Column(db.Integer,primary_key=True)
    quantity = db.Column(db.Integer)
    price = db.Column(db.Float)

    @staticmethod
    def init_db(app):
        """ Initializes the database session """
        Shopcart.logger.info('Initializing database')
        Shopcart.app = app
        # This is where we initialize SQLAlchemy from the Flask app
        db.init_app(app)
        app.app_context().push()
        db.create_all()  # make our sqlalchemy tables

    def serialize(self):
        """ Serializes a Shopcart entry into a dictionary """
        return {"user_id": self.user_id,
                "product_id": self.product_id,
                "quantity": self.quantity,
                "price": self.price}

    def deserialize(self, data):
        """
        Deserializes a Shopcart entry from a dictionary

        Args:
            data (dict): A dictionary containing the Shopcart entry data
        """
        try:
            self.user_id = data['user_id']
            self.product_id = data['product_id']
            self.quantity = data['quantity']
            self.price = data['price']
        except KeyError as error:
            raise DataValidationError('Invalid entry for Shopcart: missing ' + error.args[0])
        except TypeError as error:
            raise DataValidationError('Invalid entry for Shopcart: body of request contained' \
                                      'bad or no data')
        return self

    @staticmethod
    def find(user_id, product_id):
        """ Finds if user <user_id> has product <product_id> by it's ID """
        Shopcart.logger.info('Processing lookup for user id %s and pet id %s ...', user_id, product_id)
        return Shopcart.query.get(user_id, product_id)
