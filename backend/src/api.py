import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
from sqlalchemy.exc import SQLAlchemyError
import json
from flask_cors import CORS

from .database.models import db_drop_and_create_all, setup_db, Drink
from .auth.auth import AuthError, requires_auth

app = Flask(__name__)
setup_db(app)
CORS(app)

'''
@TODO uncomment the following line to initialize the datbase
!! NOTE THIS WILL DROP ALL RECORDS AND START YOUR DB FROM SCRATCH
!! NOTE THIS MUST BE UNCOMMENTED ON FIRST RUN
'''
db_drop_and_create_all()

## ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks')
def get_drinks():
  drinks = list(map(Drink.short, Drink.query.all()))

  return jsonify({
    "success": True,
    "drinks": drinks
  })

'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
@app.route("/drinks-detail")
@requires_auth("get:drinks-detail")
def get_drinks_detail(token):
    drinks = list(map(Drink.long, Drink.query.all()))
    result = {
        "success": True,
        "drinks": drinks
    }
    return jsonify(result)

'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def post_drink(token):
  body = request.get_json()

  title = body.get('title')
  recipe = body.get('recipe')

  print(json.dumps(recipe))
 
  new_drink = Drink(title=title, recipe=json.dumps([recipe]))
  

  try:
    new_drink.insert()
    drinks = list(map(Drink.long, Drink.query.all()))
    
    return jsonify({
      "success": True,
      "drinks": drinks
    })
  except SQLAlchemyError as error:
    print(error)
    abort(422)

'''
@TODO implement endpoint
    PATCH /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should update the corresponding row for <id>
        it should require the 'patch:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the updated drink
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def update_drink(payload, drink_id):
  body = request.get_json()

  new_title = body.get('title')
  new_recipe = body.get('recipe')

  try:
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    drink.title = new_title
    drink.new_recipe = json.dumps([new_recipe])
    drink.update()
    drinks = list(map(Drink.long, Drink.query.all()))

    return jsonify({
      "success": True,
      "drinks": drinks
    })
  except:
    abort(422)
'''
@TODO implement endpoint
    DELETE /drinks/<id>
        where <id> is the existing model id
        it should respond with a 404 error if <id> is not found
        it should delete the corresponding row for <id>
        it should require the 'delete:drinks' permission
    returns status code 200 and json {"success": True, "delete": id} where id is the id of the deleted record
        or appropriate status code indicating reason for failure
'''
@app.route('/drinks/<int:drink_id>', methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drink(payload, drink_id):

  try:
    drink = Drink.query.filter(Drink.id == drink_id).one_or_none()
    drink.delete()
    drinks = list(map(Drink.long, Drink.query.all()))

    return jsonify({
      "success": True,
      "drinks": drinks
    })
  except:
    abort(422)
## Error Handling
'''
Example error handling for unprocessable entity
'''
@app.errorhandler(422)
def unprocessable(error):
    return jsonify({
                    "success": False, 
                    "error": 422,
                    "message": "unprocessable"
                    }), 422

'''
@TODO implement error handlers using the @app.errorhandler(error) decorator
    each error handler should return (with approprate messages):
             jsonify({
                    "success": False, 
                    "error": 404,
                    "message": "resource not found"
                    }), 404

'''

'''
@TODO implement error handler for 404
    error handler should conform to general task above 
'''
@app.errorhandler(404)
def method_not_allowed(error):
  return jsonify({
    "success": False,
    "error": 404,
    "message": "Not found"
  }), 404

'''
@TODO implement error handler for AuthError
    error handler should conform to general task above 
'''
@app.errorhandler(AuthError)
def auth_error(err):
  return jsonify(err.error), err.status_code