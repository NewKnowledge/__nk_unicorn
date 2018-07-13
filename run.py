from http_wrapper import get_visual_clusters, remove_community_clusters, insert_clusters
import pandas as pd
from http_wrapper.http_utils import to_date_string


# from http_wrapper.app import req_visual_clusters
COMMUNITIES = ['world-cup', 'test-community']
START_TIME = to_date_string(pd.datetime.now() - pd.Timedelta('4d'))
STOP_TIME = to_date_string(pd.datetime.now())
IMAGE_LIMIT = 10

for community_name in COMMUNITIES:
    print('clustering community:', community_name)
    image_urls, labels = get_visual_clusters(community_name, START_TIME, STOP_TIME)

    removed = remove_community_clusters(community_name)
    print('removed', len(removed), 'rows')

    insert_clusters(community_name, image_urls, labels)
    print('inserted of', len(image_urls), 'rows')
