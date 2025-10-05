from flask import Blueprint

platforms_blueprint = Blueprint("platforms", __name__)

@platforms_blueprint.route("/", methods=['GET'])
def getAllPlatforms():
    return "Get all platforms"

@platforms_blueprint.route("/add", methods=['POST'])
def addPlatform():
    return "Add Platform"

@platforms_blueprint.route("/get/:id", methods=['GET'])
def getPlatform():
    return "Get platform"

@platforms_blueprint.route("/edit/:id", methods=['PUT'])
def editPlatform():
    return "Edit Platform"

@platforms_blueprint.route("/delete", methods=['DELETE'])
def deletePlatform():
    return "Delete Platform"

