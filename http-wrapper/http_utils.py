''' Utility functions for parsing dates, json, etc. '''
import json
import sys
from datetime import datetime, timedelta
from functools import wraps

import numpy as np
import pandas as pd
from flask import Response, request

from config import API_PASSWORD

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


def log(*args, **kwargs):
    print(*args, file=sys.stderr, **kwargs)


def parse_date_string(date_string):
    try:
        date_string = date_string.replace('T', ' ')
        date_string = date_string.replace('_', ' ')
        return datetime.strptime(date_string, TIME_FORMAT)
    except ValueError as err:
        print('error:', err)
        raise Exception('Must give dates in YYYY-MM-DD HH:mm:SS format')


def to_date_string(dtime):
    # TODO add ability to round to given time resolution, here an hour
    dtime = dtime - timedelta(minutes=dtime.minute,
                              seconds=dtime.second,
                              microseconds=dtime.microsecond)
    return dtime.strftime(TIME_FORMAT)


class NumpyEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, np.ndarray):
            return obj.tolist()
        return json.JSONEncoder.default(self, obj)


class PandasEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, pd.DataFrame):
            return [row.to_dict() for _, row in obj.iterrows()]
        if isinstance(obj, np.ndarray):
            return NumpyEncoder.default(self, obj)
        return json.JSONEncoder.default(self, obj)


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
    return username == 'admin' and password == API_PASSWORD


def authenticate():
    """Sends a 401 response that enables basic auth"""
    return Response(
        'Could not verify your access level for that URL.\n'
        'You have to login with proper credentials', 401,
        {'WWW-Authenticate': 'Basic realm="Login Required"'})
