
[![Build Status](https://travis-ci.org/NYUDevOps-Fall18-Shopcarts/shopcarts.svg?branch=master)](https://travis-ci.org/NYUDevOps-Fall18-Shopcarts/shopcarts)
[![codecov](https://codecov.io/gh/NYUDevOps-Fall18-Shopcarts/shopcarts/branch/master/graph/badge.svg)](https://codecov.io/gh/NYUDevOps-Fall18-Shopcarts/shopcarts)

# Shopcarts
Shopcart Development:

# Description
Shopcarts is a Microservice built using 12 factor standards and accessible via RESTful API calls. Shopcarts service provides access to shopcarts of e-commerce website by RESTful API calls to Create, Read, Update, Delete, List and Query shopcarts.Shopcarts API provides service to keep track of resources in warehouse. It provides count of each inventory item in warehouse and also holds it's condition i.e. whether it is 'new', 'used' or 'open-box'.

The shopcarts API provides service to keep track of resources in the shopcart.

	Description
	JSON Format
	Add product to the shopcart
	List product in the shopcart
	Read product in the shopcart
	Update product in the shopcart
	Delete product in the shopcart
	Query product in the shopcart based on User ID
	Action- Delete the product from all the shopcarts(Use case : product goes out of availability)

# Prerequisite Installation using Vagrant

The easiest way to use this lab is with Vagrant and VirtualBox. if you don't have this software the first step is down download and install it.

Download VirtualBox

Download Vagrant

Then all you have to do is clone this repo and invoke vagrant:

git clone https://github.com/NYUDevOps-Fall18-Shopcarts/shopcarts.git
cd shopcarts
vagrant up
vagrant ssh
cd /vagrant
You can now run nosetests to run the tests.It is always better to a follow TDD (Test Driven Development)

# What's featured in the project?
* app/service.py -- the main Service using Python Flask
* app/model.py -- the data model using SQLAlchemy
* tests/test_server.py -- test cases against the service
* tests/test_model.py -- test cases against the shopcart model


# Table Schema
user_id = db.Column(db.Integer,primary_key=True)

product_id = db.Column(db.Integer,primary_key=True)

quantity = db.Column(db.Integer)

price = db.Column(db.Float)

#Attributes:

product_id (int)    - the product-id of a Product used to uniquely identify it
user_id (int)       - the user-id of the User which uniquely identifies the User
quantity (int)     - number of items User wants to buy of that particular product
price(float)       - cost of one item of the Product

#Paths:

#
METHOD/URL	                                                         DESCRIPTION
POST/shopcarts	 	                                               Create a record
GET/shopcarts/<int:user_id>		                                  List the product
PUT/shopcarts/<int:user_id>/product/<int:product_id>	        Update the product
GET/shopcarts/<int:user_id>/total		            Get the total amount to be payed
DELETE/shopcarts/<int:user_id>/<int:product_id>		  Delete an item from the cart
DELETE/shopcarts/<int:user_id>	                      Clear shopcart of the user
GET/shopcarts/<int:user_id>/product/<int:product_id>	   Get info of the product
