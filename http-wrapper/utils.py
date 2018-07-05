import os
from functools import wraps

import psycopg2
from retrying import retry
from flask import Response, request
from config import SQL_HOST, SQL_PASSWORD, SQL_PORT, SQL_USER

POSTGRES_USER = os.getenv('POSTGRES_USER', 'postgres')
POSTGRES_HOST = os.getenv('POSTGRES_HOST', 'localhost')
POSTGRES_HOST_SEED = os.getenv('POSTGRES_HOST_SEED', 'localhost')

# authorized_user = {
#     "user": os.getenv("API_USER", "admin"),
#     "pass": os.getenv("API_PASSWORD")
# }

# if authorized_user["user"] is "admin":
#     print("[WARN]: Using default username")

# if authorized_user["pass"] is None:
#     print("[WARN]: authorized_user password is not set")


# def requires_auth(f):
#     @wraps(f)
#     def decorated(*args, **kwargs):
#         auth = request.authorization
#         if not auth or not check_auth(auth.username, auth.password):
#             return authenticate()
#         return f(*args, **kwargs)
#     return decorated


# def check_auth(username, password):
#     """This function is called to check if a username /
#     password combination is valid.
#     """
#     return username == authorized_user["user"] and password == authorized_user["pass"]


# def authenticate():
#     """Sends a 401 response that enables basic auth"""
#     return Response(
#         'Could not verify your access level for that URL.\n'
#         'You have to login with proper credentials', 401,
#         {'WWW-Authenticate': 'Basic realm="Login Required"'})


def execute_query(db_connection, query, query_params={}):
    print('executing query')
    with db_connection as conn:
        with conn.cursor() as cursor:
            cursor.execute(query, query_params)
            if cursor.description is not None:
                return list(cursor.fetchall())
            else:   
                return True


@retry(wait_exponential_multiplier=1000, wait_exponential_max=10000,
       stop_max_attempt_number=5)
def connect(seed=False):
    host = POSTGRES_HOST_SEED if seed else POSTGRES_HOST
    return psycopg2.connect(
        host=host,
        dbname=POSTGRES_USER,
        user=POSTGRES_USER,
        port=5432,
        sslmode='allow')
