import os

import pandas as pd

from http_wrapper import get_visual_clusters, insert_clusters, remove_community_clusters
from http_wrapper.http_utils import to_date_string

# TODO query social db for all communities to cluster
COMMUNITIES = os.getenv('COMMUNITIES', ['world-cup', 'test-community'])
START_TIME = os.getenv('START_TIME', to_date_string(pd.datetime.now() - pd.Timedelta('14d')))
STOP_TIME = os.getenv('STOP_TIME', to_date_string(pd.datetime.now()))
IMAGE_LIMIT = os.getenv('IMAGE_LIMIT', 1000)

for community_name in COMMUNITIES:
    try:
        print('clustering community:', community_name)
        result = get_visual_clusters(community_name, START_TIME, STOP_TIME, image_limit=IMAGE_LIMIT)
        if isinstance(result, str):
            print(result)
        else:
            image_urls, labels = result

        removed = remove_community_clusters(community_name)
        print('removed', len(removed), 'rows')

        insert_clusters(community_name, image_urls, labels)
        print('inserted', len(image_urls), 'rows')
    except Exception as err:
        print('community', community_name, 'failed with error:', err)
