#!/usr/bin/python3
import time
import sys

from flask import Flask, request, render_template
from json import dumps, loads

import pandas as pd
import numpy as np
from keras.applications.inception_v3 import InceptionV3
from nk_unicorn import *


class UnicornRestListener():
    ''' **Class for managing UNICORN config**
        UnicornRestListener accepts an image path or URL
        and outputs a json file with the character and object
        information that has been deteected.
    '''

    def __init__(self):
        self.unicorn = Unicorn()
        self.unicorn.model = InceptionV3(weights='imagenet', include_top=False)
        self.cluster_cutoff = 2

    def cluster_stats(self, cluster_data):
        ''' produce some stats about the cluster outcome
        '''
        key_clusters_df = pd.concat(
            g for _, g in cluster_data.groupby('pred_class')
            if len(g) >= self.cluster_cutoff
        )

        cluster_stats_df = pd.DataFrame()

        for i in key_clusters_df['pred_class'].unique():
            temp_data = key_clusters_df[key_clusters_df['pred_class'] == i]

            cluster_stats_df = cluster_stats_df.append(
                {'cluster_size': len(temp_data),
                 'mean_variance': np.mean(temp_data.iloc[:, 2:].var(axis=0))
                 }, ignore_index=True
            )

        return cluster_stats_df

    def find_clusters(self, image_paths):
        ''' analyze a given image and return text and detected objects
        '''

        unicorn_result = self.unicorn.cluster_images(image_paths)

        return unicorn_result


# Init UNICORN Class def'd above
listener = UnicornRestListener()
# Hack-y work around for ensuring Keras Tensor map is available in the global scope.
# See https://github.com/keras-team/keras/issues/2397 for more info
listener.find_clusters(
    ["http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg",
     "http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg",
     "http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg",
     "http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg",
     "http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg",
     "http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg"]
)

# Init Flask
app = Flask(__name__)


@app.route('/')
# @requires_auth
def index():
    ''' **Demo Landing Route**
    '''
    return render_template('index.html')

# to have a nice web demo we need code here to take a list of
# paths POSTed as a string and clean it up
# @app.route("/demo-fileupload", methods=['POST'])
# # @requires_auth
# def demo_cluster_uploaded_images():
#     ''' **Demo Results Route**
#         Listen for an image url being POSTed on root.
#     '''
#     request.get_data()

#     image_paths = request.form['image_paths']

#     result = listener.find_clusters(image_paths)

#     # Converting to pd.DataFrame seemed to be the fastest way to get results to a http table
#     return render_template(
#         'display.html', image_paths=image_paths,
#         table=pd.DataFrame.from_dict(result).to_html(),
#     )


@app.route("/test-fileupload", methods=['POST'])
# @requires_auth
def test_cluster_uploaded_images():
    ''' **Route for testing UNICORN as a http/web service**
        Listen for a JSONified dict being POSTed on root where
        the only entry is a key-value pair where the key is
        'image_paths' and the value is a list of of image urls
    '''
    request.get_data()

    image_paths = loads(request.get_json())['image_paths']

    result, processed_feature_data = listener.find_clusters(image_paths)

    cluster_stats_df = listener.cluster_stats(
        result.join(processed_feature_data)
    )

    return app.response_class(
        cluster_stats_df.to_json(),
        content_type='application/json')
