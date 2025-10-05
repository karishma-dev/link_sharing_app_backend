from flask import Blueprint

users_blueprint = Blueprint("users", __name__)

@users_blueprint.route("/", methods=['GET'])
def getAllUsers():
    return "Get all users"

@users_blueprint.route("/:id", methods=['GET'])
def getUser():
    return "Get user"

@users_blueprint.route("/:id", methods=['PUT'])
def editUser():
    return "Edit user"

@users_blueprint.route("/delete", methods=['DELETE'])
def deleteUser():
    return "Delete user"

