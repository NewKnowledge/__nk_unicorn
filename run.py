import os
import logging

import pandas as pd

from http_wrapper import get_community_names, get_visual_clusters, insert_clusters, remove_community_clusters
from http_wrapper.http_utils import to_date_string

# logging.basicConfig(level=logging.DEBUG)
logging.basicConfig(level=logging.INFO)

START_TIME = os.getenv('START_TIME', to_date_string(pd.datetime.now() - pd.Timedelta('14d')))
STOP_TIME = os.getenv('STOP_TIME', to_date_string(pd.datetime.now()))
IMAGE_LIMIT = os.getenv('IMAGE_LIMIT', 4000)
NUM_CHANNELS = os.getenv('NUM_CHANNELS', 64)

communities = get_community_names()

for community_name in communities:
    try:
        logging.info(f'clustering community: {community_name}')
        image_urls, labels = get_visual_clusters(community_name, START_TIME, STOP_TIME,
                                                 image_limit=IMAGE_LIMIT,
                                                 n_channels=NUM_CHANNELS)

        if not image_urls:
            # Skip to next community if we didn't get any images
            continue

        removed = remove_community_clusters(community_name)
        logging.info(f'removed {len(removed)} rows')

        insert_clusters(community_name, image_urls, labels)
        logging.info(f'inserted {len(image_urls)} rows')
    except Exception as err:
        logging.exception(f'community {community_name} failed')
