''' Utility functions for parsing dates, json, etc. '''
import json
from datetime import datetime, timedelta

import numpy as np
import pandas as pd

TIME_FORMAT = '%Y-%m-%d %H:%M:%S'


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
