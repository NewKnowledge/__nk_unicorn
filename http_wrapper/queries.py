import os
import logging

import numpy as np
from sqlalchemy import text

from nk_unicorn import ImagenetModel, Unicorn

from .config import DB_CONFIG
from .db_utils import get_connection
from .http_utils import log

unicorn = Unicorn()
image_net = ImagenetModel()
# NOTE: we force the imagenet model to load in the same scope as flask app to avoid tensorflow weirdness
image_net.model.predict(np.zeros((1, 299, 299, 3)))
log('imagenet loaded')


def insert_clusters(community_name, urls, labels):
    connection = get_connection(DB_CONFIG['cluster'])
    # image_url, community_name, cluster_label
    values = [str(tupl) for tupl in zip(urls, [community_name] * len(urls), labels)]
    query = text('INSERT INTO image_clusters.cluster_labels (image_url, community_name, cluster_label) \
                    VALUES' + ', '.join(values) + ';')
    connection.execute(query, community_name=community_name)
    # TODO need to commit after insert?


def remove_community_clusters(community_name):
    connection = get_connection(DB_CONFIG['cluster'])
    query = text('''delete
        from image_clusters.cluster_labels as labels
        where labels.community_name=:community_name
        returning *
        ''')
    return [dict(res) for res in connection.execute(query, community_name=community_name)]


def get_community_names():
    connection = get_connection(DB_CONFIG['social'])
    query = text('select distinct cp.community_name from social.communities_posts cp')
    return [res[0] for res in connection.execute(query)]


def get_community_image_urls(community_name, start_time, stop_time, image_limit=None):

    query_params = dict(community_name=community_name, start_time=start_time, stop_time=stop_time)

    limit_statement = ''
    if image_limit:
        limit_statement = 'limit :image_limit'
        query_params['image_limit'] = image_limit

    connection = get_connection(DB_CONFIG['social'])
    query = text(f'''select distinct l.url
        from social.links l
        join social.posts_links pl on pl.link_id=l.link_id
        join social.posts p on pl.post_id=p.post_id
        join social.communities_posts cp on cp.post_id=p.post_id
        where l.type='image'
        and cp.community_name = :community_name
        and p.published_at >= :start_time
        and p.published_at <= :stop_time
        {limit_statement};
        ''')
    return [res[0] for res in connection.execute(query, **query_params)]


def get_visual_clusters(community_name, start_time, stop_time, image_limit=None):

    assert isinstance(start_time, str) and isinstance(stop_time, str)
    image_urls = get_community_image_urls(community_name, start_time, stop_time, image_limit=image_limit)

    if image_limit:
        assert len(image_urls) <= int(image_limit)

    if not image_urls:
        logging.info(f'No images found in {community_name} community between {start_time} and {stop_time}')
        return [], None

    # NOTE that image_urls returned here may be shorter than input if some urls failed
    num_urls = len(image_urls)
    array_data, image_urls = image_net.get_features_from_urls(image_urls)
    num_dropped = num_urls - len(image_urls)
    if num_dropped > 0:
        logging.info(f'unable to retreive {num_dropped} urls out of {num_urls}')

    assert array_data.shape[0] == len(image_urls)

    labels = unicorn.cluster(array_data)

    return image_urls, labels
    # return {url: lbl for url, lbl in zip(image_urls, labels)}
