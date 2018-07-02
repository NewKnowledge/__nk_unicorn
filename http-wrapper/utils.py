from os import getenv
from functools import wraps

from flask import Response, request

authorized_user = {
    "user": getenv("API_USER", "admin"),
    "pass": getenv("API_PASSWORD")
}

if authorized_user["user"] is "admin":
    print("[WARN]: Using default username")

if authorized_user["pass"] is None:
    print("[WARN]: authorized_user password is not set")


def requires_auth(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        auth = request.authorization
        if not auth or not check_auth(auth.username, auth.password):
            return authenticate()
        return f(*args, **kwargs)
    return decorated


def check_auth(username, password):
    """This function is called to check if a username /
    password combination is valid.
    """
    return username == authorized_user["user"] and password == authorized_user["pass"]


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})