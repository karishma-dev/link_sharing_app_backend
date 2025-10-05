from flask import Blueprint

admin_blueprint = Blueprint("admin", __name__)

@admin_blueprint.route("/login", methods=['POST'])
def login():
    return "Login"

@admin_blueprint.route("/reset-password", methods=['POST'])
def resetPassword():
    return "Reset admin Password"