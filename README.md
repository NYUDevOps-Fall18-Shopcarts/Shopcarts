
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

# Attributes:

product_id (int)    - the product-id of a Product used to uniquely identify it

user_id (int)       - the user-id of the User which uniquely identifies the User

quantity (int)     - number of items User wants to buy of that particular product

price(float)       - cost of one item of the Product

# Paths:

# METHOD/URL	                                              -----                                  DESCRIPTION

POST/shopcarts                                              -----                                 Create a record

GET/shopcarts/<int:user_id>		                              -----                                 List the product

PUT/shopcarts/<int:user_id>/product/<int:product_id>	      -----                                 Update the product

GET/shopcarts/<int:user_id>/total		                        -----                                 Get the total amount to be payed

DELETE/shopcarts/<int:user_id>/<int:product_id>		          -----                                 Delete an item from the cart

DELETE/shopcarts/<int:user_id>	                            -----                                 Clear shopcart of the user

GET/shopcarts/<int:user_id>/product/<int:product_id>	      -----                                 Get info of the product

# Structure of application

Procfile - Contains the command to run when application starts on Bluemix. It is represented in the form web: <command> where <command> in this sample case is to run the py command and passing in the the server.py script.

requirements.txt - Contains the external python packages that are required by the application. These will be downloaded from the python package index and installed via the python package installer (pip) during the buildpack's compile stage when you execute the cf push command. In this sample case we wish to download the Flask package at version 1.0.2 and Cloudant package at version 2.9.0.

runtime.txt - Controls which python runtime to use. In this case we want to use Python 2.7.14.

README.md - this readme.

manifest.yml - Controls how the app will be deployed in Bluemix and specifies memory and other services like Redis that are needed to be bound to it.

service - the python package that contains fthe applciation. This is implemented as a simple Flask-RESTful application. The routes are defined in the application using the api.add_resource() calls. This application has a / route and a /pets route defined. The application deployed to IBM Cloud needs to listen to the port defined by the VCAP_APP_PORT environment variable as seen here:

port = os.getenv('VCAP_APP_PORT', '5000')
if __name__ == "__main__":
    app.run(host='0.0.0.0', port=int(port))
This is the port given to your application so that http requests can be routed to it. If the property is not defined then it falls back to port 5000 allowing you to run this sample application locally.
