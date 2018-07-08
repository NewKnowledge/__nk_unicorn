''' Flask app for unicorn clustering service '''

import json
import markdown
import pandas as pd
import numpy as np
from flask import Flask, Markup, jsonify, render_template, request

from http_utils import to_date_string, PandasEncoder
from nk_unicorn import ImagenetModel, Unicorn
from queries import get_community_image_urls, get_community_names
import sys


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
    start_time = request.args.get('start_time', to_date_string(pd.datetime.now() - pd.Timedelta('2d')))
    image_limit = request.args.get('image_limit', None)

    print('getting list of urls for community named', community_name,
          'from', start_time, 'to', stop_time, file=sys.stderr)

    image_urls = get_community_image_urls(community_name, start_time, stop_time)

    if not image_urls:
        return f'No images found in {community_name} community between {start_time} and {stop_time}'

    if image_limit:
        # pick a random `image_limit` images to use for clustering
        inds = np.random.permutation(len(image_urls))[:image_limit]
        image_urls = image_urls[inds]

    # print('community image urls:', image_urls, file=sys.stderr)
    print('len of results of community image url query:', len(image_urls), file=sys.stderr)
    # NOTE that image_urls returned here may be shorter than input if some urls failed
    array_data, image_urls = image_net.get_features_from_urls(image_urls)
    print('new community image urls len:', len(image_urls), file=sys.stderr)

    assert array_data.shape[0] == len(image_urls)

    print('clustering image array of shape', array_data.shape, file=sys.stderr)
    clusters = unicorn.cluster(array_data)

    # TODO option to return dataframe
    urls_by_label = pd.DataFrame([dict(url=url, label=label) for url, label in zip(image_urls, clusters)])
    urls_by_label = {label: df['url'].values for label, df in urls_by_label.groupby('label', as_index=False)}

    # print('urls by label:', urls_by_label, file=sys.stderr)

    return json.dumps(urls_by_label, cls=PandasEncoder)


if __name__ == "__main__":
    app.run(debug=True)

# class UnicornRestListener():
#     ''' **Class for managing UNICORN config**
#         UnicornRestListener accepts an image path or URL
#         and outputs a json file with the character and object
#         information that has been deteected.
#     '''

#     def __init__(self):
#         self.unicorn = Unicorn()
#         self.unicorn.model = InceptionV3(weights='imagenet', include_top=False)
#         self.cluster_cutoff = 2

#     def cluster_stats(self, cluster_data):
#         ''' produce some stats about the cluster outcome
#         '''
#         key_clusters_df = pd.concat(
#             g for _, g in cluster_data.groupby('cluster_label')
#             if len(g) >= self.cluster_cutoff
#         )

#         cluster_stats_df = pd.DataFrame()

#         for i in key_clusters_df['cluster_label'].unique():
#             temp_data = key_clusters_df[key_clusters_df['cluster_label'] == i]

#             cluster_stats_df = cluster_stats_df.append(
#                 {'cluster_size': len(temp_data),
#                  'mean_variance': np.mean(temp_data.iloc[:, 2:].var(axis=0))
#                  }, ignore_index=True
#             )

#         return cluster_stats_df

#     def find_clusters(self, image_paths):
#         ''' analyze a given image and return text and detected objects
#         '''

#         unicorn_result = self.unicorn.cluster_images(image_paths)

#         return unicorn_result


# @app.route('/visual-clusters/<int:community_name>')
# def req_image_clusters(community_name: int):

#     stop_time = request.args.get('stop_time', to_date_string(pd.datetime.now()))
#     start_time = request.args.get('start_time', to_date_string(pd.datetime.now() - pd.Timedelta('2d')))
#     cluster_limit = int(request.args.get('cluster_limit', 10))
#     url_limit = int(request.args.get('url_limit', 100))
#     pretty = request.args.get('pretty', False)

#     res = get_image_clusters(community_name, start_time, stop_time,
#                              cluster_limit=cluster_limit,
#                              url_limit=url_limit,
#                              )

#     if pretty:
#         res = json.loads(json.dumps(res, cls=PandasEncoder))
#         return jsonify(res)
#     return json.dumps(res, cls=PandasEncoder, indent=2)


# @app.route('/visual-clusters/<int:community_name>')
# def test_cluster_uploaded_images():
#     ''' **Route for testing UNICORN as a http/web service**
#         Listen for a JSONified dict being POSTed on root where
#         the only entry is a key-value pair where the key is
#         'image_paths' and the value is a list of of image urls
#     '''
#     request.get_data()

#     image_paths = loads(request.get_json())['image_paths']

#     result, processed_feature_data = listener.find_clusters(image_paths)

#     cluster_stats_df = listener.cluster_stats(
#         result.join(processed_feature_data)
#     )

#     return app.response_class(
#         cluster_stats_df.to_json(),
#         content_type='application/json')


# # Init UNICORN Class def'd above
# listener = UnicornRestListener()
# # Hack-y work around for ensuring Keras Tensor map is available in the global scope.
# # See https://github.com/keras-team/keras/issues/2397 for more info
# listener.find_clusters(
#     ["http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg",
#      "http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg",
#      "http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg",
#      "http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg",
#      "http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg",
#      "http://i0.kym-cdn.com/photos/images/facebook/001/253/011/0b1.jpg"]
# )
# @app.route('/')
# @requires_auth
# def index():
#     ''' **Demo Landing Route**
#     '''
    # return render_template('index.html')

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
