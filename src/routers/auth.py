from flask import Blueprint

auth_blueprint = Blueprint('auth', __name__)

@auth_blueprint.route("/login", methods=['POST'])
def login():
    return "Login"

@auth_blueprint.route("/signup", methods=['POST'])
def signup():
    return "Signup"

@auth_blueprint.route("/verify-email-signup", methods=['POST'])
def verifyEmailSignup():
    return "Verify Email signup"


@auth_blueprint.route("/forgot-password", methods=['POST'])
def forgotPassword():
    return "Forgot Password"

@auth_blueprint.route("/reset-password", methods=['POST'])
def resetPassword():
    return "Reset Password"

@auth_blueprint.route("/change-password", methods=['POST'])
def changePassword():
    return "Change Password"