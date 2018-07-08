''' Flask app for unicorn clustering service '''

import json
import sys

import markdown
import numpy as np
import pandas as pd
from flask import Flask, Markup, jsonify, render_template, request

from http_utils import PandasEncoder, to_date_string
from nk_unicorn import ImagenetModel, Unicorn
from queries import get_community_image_urls, get_community_names, remove_community_clusters, insert_clusters

unicorn = Unicorn()
image_net = ImagenetModel()
# NOTE: we force the imagenet model to load in the same scope as flask app to avoid tensorflow weirdness
image_net.model.predict(np.zeros((1, 299, 299, 3)))
print('imagenet loaded')

app = Flask(__name__)


@app.route('/')
def homepage():
    with open('README.md') as readme:
        content = readme.read()

    content = Markup(markdown.markdown(content))
    return render_template('index.html', content=content)


@app.route('/community-names')
def req_community_names():
    return jsonify(get_community_names())


@app.route('/visual-clusters/<community_name>')
def req_visual_clusters(community_name):
    # localhost:5000/visual-clusters/world-cup?start_time=2018-07-06_18:00:00

    stop_time = request.args.get('stop_time', to_date_string(pd.datetime.now()))
    start_time = request.args.get('start_time', to_date_string(pd.datetime.now() - pd.Timedelta('3d')))
    image_limit = request.args.get('image_limit', 600)

    print('getting list of urls for community named', community_name,
          'from', start_time, 'to', stop_time, file=sys.stderr)

    # TODO pass limit to community images query
    image_urls = get_community_image_urls(community_name, start_time, stop_time)

    if not image_urls:
        return f'No images found in {community_name} community between {start_time} and {stop_time}'

    if image_limit:
        # pick a random `image_limit` images to use for clustering
        np.random.shuffle(image_urls)
        image_urls = image_urls[:image_limit]

    # print('community image urls:', image_urls, file=sys.stderr)
    print('len of results of community image url query:', len(image_urls), file=sys.stderr)
    # NOTE that image_urls returned here may be shorter than input if some urls failed
    array_data, image_urls = image_net.get_features_from_urls(image_urls)
    print('new community image urls len:', len(image_urls), file=sys.stderr)

    assert array_data.shape[0] == len(image_urls)

    print('clustering image array of shape', array_data.shape, file=sys.stderr)
    labels = unicorn.cluster(array_data)

    # TODO option to return dataframe
    urls_by_label = pd.DataFrame([dict(url=url, label=label) for url, label in zip(image_urls, labels)])
    urls_by_label = {label: df['url'].values for label, df in urls_by_label.groupby('label')}

    removed = remove_community_clusters(community_name)
    print('result from removing community cluster labels:', removed, file=sys.stderr)

    insert_clusters(community_name, image_urls, labels)
    print('insert successful', file=sys.stderr)

    return jsonify(json.loads(json.dumps(urls_by_label, cls=PandasEncoder)))
    # json.dumps(urls_by_label, cls=PandasEncoder)


if __name__ == "__main__":
    app.run(debug=True)
