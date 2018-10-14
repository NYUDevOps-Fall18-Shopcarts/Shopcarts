"""
Models for Pet Demo Service

All of the models are stored in this module

Models
------
Shopcart - A Shopcart used by each User

Attributes:
-----------
productId (int)    - the product-id of a Product used to uniquely identify it
userId (int)       - the user-id of the User which uniquely identifies the User
quantity (int)     - number of items User wants to buy of that particular product
price(float)       - cost of one item of the Product

"""
import logging
from flask_sqlalchemy import SQLAlchemy

# Create the SQLAlchemy object to be initialized later in init_db()
db = SQLAlchemy()

class Shopcart(db.Model):
    """
    Class that represents a Shopcart

    This version uses a relational database for persistence which is hidden
    from us by SQLAlchemy's object relational mappings (ORM)
    """

    logger = logging.getLogger(__name__)
    app = None

    # Table Schema
    userId = db.Column(db.Integer,primary_key=True)
    productId = db.Column(db.Integer,primary_key=True)
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
