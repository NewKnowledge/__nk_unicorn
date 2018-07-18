''' Flask app for unicorn clustering service '''

import json
import sys

import markdown
import numpy as np
import pandas as pd
from flask import Flask, Markup, jsonify, render_template, request


from .http_utils import PandasEncoder, log, requires_auth, to_date_string
from .queries import (get_community_image_urls, get_community_names,
                      insert_clusters, remove_community_clusters, get_visual_clusters)


app = Flask(__name__)


@app.route('/')
def homepage():
    with open('README.md') as readme:
        content = readme.read()

    content = Markup(markdown.markdown(content))
    return render_template('index.html', content=content)


@app.route('/community-names')
@requires_auth
def req_community_names():
    return jsonify(get_community_names())


@app.route('/visual-clusters/<community_name>')
@requires_auth
def req_visual_clusters(community_name):
    # localhost:5000/visual-clusters/world-cup?start_time=2018-07-06_18:00:00

    stop_time = request.args.get('stop_time', to_date_string(pd.datetime.now()))
    start_time = request.args.get('start_time', to_date_string(pd.datetime.now() - pd.Timedelta('4d')))
    image_limit = int(request.args.get('image_limit', 8000))

    log('getting list of urls for community named', community_name, 'from', start_time, 'to', stop_time)

    labeled_images = get_visual_clusters(community_name, start_time, stop_time, image_limit)

    return jsonify(labeled_images)


if __name__ == "__main__":
    app.run(debug=True)
