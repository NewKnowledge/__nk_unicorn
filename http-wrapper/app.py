#!/usr/bin/python3
import time

from flask import Flask, request, render_template
from json import dumps, loads

import pandas as pd
from keras.applications.inception_v3 import InceptionV3
from nk_unicorn import *
from utils import requires_auth


class UnicornRestListener():
    """ **Class for managing UNICORN config**
        UnicornRestListener accepts an image path or URL
        and outputs a json file with the character and object
        information that has been deteected.
    """

    def __init__(self):
        self.unicorn = Unicorn()
        self.unicorn.model = InceptionV3(weights='imagenet', include_top=False)

    def find_clusters(self, image_paths):
        """ analyze a given image and return text and detected objects
        """
        start = time.time()

        unicorn_result = self.unicorn.cluster_images(image_paths)

        print(
            "The whole script took %f seconds to execute"
            % (time.time() - start))
        return unicorn_result.to_json()


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
    """ **Demo Landing Route**
    """
    return render_template('index.html')


@app.route("/demo-fileupload", methods=['POST'])
# @requires_auth
def demo_cluster_uploaded_images():
    ''' **Demo Results Route**
        Listen for an image url being POSTed on root.
    '''
    request.get_data()

    image_paths = request.form['image_paths']

    result = listener.find_clusters(image_paths)

    # Converting to pd.DataFrame seemed to be the fastest way to get results to a http table
    return render_template(
        'display.html', image_paths=image_paths,
        table=pd.DataFrame.from_dict(result).to_html(),
    )


@app.route("/test-fileupload", methods=['POST'])
# @requires_auth
def test_cluster_uploaded_images():
    ''' **Route for using UNICOR as a http/web service**
        Listen for an image url being POSTed on root.
    '''
    request.get_data()

    image_paths = loads(request.get_json())['image_paths']

    result = listener.find_clusters(image_paths)

    return app.response_class(result, content_type='application/json')


@app.route("/fileupload", methods=['POST'])
# @requires_auth
def cluster_uploaded_images():
    ''' **Route for using UNICOR as a http/web service**
        Listen for an image url being POSTed on root.
    '''
    request.get_data()

    image_paths = loads(request.get_json())['image_paths']

    result = listener.find_clusters(image_paths)

    return app.response_class(result, content_type='application/json')
