import os

from cachetools.func import ttl_cache
from sqlalchemy import select, text

from config import DB_CONFIG
from db_utils import get_connection

CACHE_TTL = os.getenv('CACHE_TTL', 3600)


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


@ttl_cache(ttl=CACHE_TTL)
def get_community_names():
    connection = get_connection(DB_CONFIG['social'])
    query = text('select distinct cp.community_name from social.communities_posts cp')
    return [res[0] for res in connection.execute(query)]


@ttl_cache(ttl=CACHE_TTL)
def get_community_image_urls(community_name, start_time, stop_time):
    # TODO assert timestamps are strings
    connection = get_connection(DB_CONFIG['social'])
    query = text('''select distinct l.url
        from social.links l
        join social.posts_links pl on pl.link_id=l.link_id
        join social.posts p on pl.post_id=p.post_id
        join social.communities_posts cp on cp.post_id=p.post_id 
        where l.type='image' 
        and cp.community_name = :community_name
        and p.published_at >= :start_time 
        and p.published_at <= :stop_time;
        ''')
    query_params = dict(community_name=community_name, start_time=start_time, stop_time=stop_time)
    return [res[0] for res in connection.execute(query, **query_params)]
