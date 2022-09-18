import os
from flask import Flask, request, jsonify, abort
from sqlalchemy import exc
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
!! Running this funciton will add one
'''
# creates required schema
db_drop_and_create_all()

# ROUTES
'''
@TODO implement endpoint
    GET /drinks
        it should be a public endpoint
        it should contain only the drink.short() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
# get open drink detail


@app.route('/')
@app.route('/drinks')
def pub_drinks():
    drinks = Drink.query.order_by(Drink.id).all()
    shorts = [drink.short() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": shorts
    })


'''
@TODO implement endpoint
    GET /drinks-detail
        it should require the 'get:drinks-detail' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drinks} where drinks is the list of drinks
        or appropriate status code indicating reason for failure
'''
# get Insider  drink detail


@app.route('/drinks-detail')
@requires_auth("get:drinks-detail")
def drink_detail(payload):
    drinks = Drink.query.order_by(Drink.id).all()
    longs = [drink.long() for drink in drinks]
    return jsonify({
        "success": True,
        "drinks": longs
    })


'''
@TODO implement endpoint
    POST /drinks
        it should create a new row in the drinks table
        it should require the 'post:drinks' permission
        it should contain the drink.long() data representation
    returns status code 200 and json {"success": True, "drinks": drink} where drink an array containing only the newly created drink
        or appropriate status code indicating reason for failure
'''

# creates or posts new drink


@app.route('/drinks', methods=['POST'])
@requires_auth("post:drinks")
def post_drink(payload):
    body = request.get_json()
    # inputs validation
    if ("title" or "recipe") not in body:
        abort(400)
    recipes = (body["recipe"])
    # handles single ingredients case
    if len(recipes) == 1:
        entry = [{"color": recipes[0]["color"], "name":recipes[0]
                  ["name"], "parts":recipes[0]["parts"]}]
    # handles multiple ingredients case
    elif len(recipes) > 1:
        entry = [{"color": recipe["color"], "name":recipe["name"],
                  "parts":recipe["parts"]} for recipe in recipes]
    # converts list to json
    new_recipe = json.dumps(entry)
    drink = Drink(title=body["title"], recipe=new_recipe)
    try:
        drink.insert()
    except:
        abort(422)
        drink.rollback()
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


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


@app.route('/drinks/<int:id>', methods=['PATCH'])
@requires_auth("patch:drinks")
def patch_drink(payload, id):
    body = request.get_json()
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404)
    # validates input
    if "title" in body:
        drink.title = body["title"]
    if "recipe" in body:
        recipes = body["recipe"]
        # handle single ingredient case
        if len(recipes) == 1:
            entry = [{"color": recipes[0]["color"], "name":recipes[0]
                      ["name"], "parts":recipes[0]["parts"]}]
        # handle multiple ingredient case
        elif len(recipes) > 1:
            entry = [{"color": recipe["color"], "name":recipe["name"],
                      "parts":recipe["parts"]} for recipe in recipes]
        # converts list to json
        new_recipe = json.dumps(entry)
        drink.recipe = new_recipe
    try:
        drink.update()
    except:
        abort(422)
        drink.rollback()
    return jsonify({
        "success": True,
        "drinks": [drink.long()]
    })


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


@app.route('/drinks/<int:id>', methods=['DELETE'])
@requires_auth("delete:drinks")
def delete_drink(payload, id):
    drink = Drink.query.filter_by(id=id).one_or_none()
    if drink is None:
        abort(404)
    try:
        drink.delete()
    except:
        abort(422)
        drink.rollback()
    return jsonify({
        "success": True,
        "delete": id
    })


# Error Handling
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
def not_found(error):
    return jsonify({
        "success": False,
        "error": 404,
        "message": "resource not found"
    }), 404


'''
@TODO implement error handler for AuthError
    error handler should conform to general task above
'''


@app.errorhandler(401)
def Unauthorized(error):
    return jsonify({
        "success": False,
        "error": 401,
        "message": "user not Authenticated"
    }), 401


@app.errorhandler(403)
def Forbidden(error):
    return jsonify({
        "success": False,
        "error": 403,
        "message": "resource forbidden"
    }), 403
