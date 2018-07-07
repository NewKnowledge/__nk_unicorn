from sqlalchemy import select, text
from db_utils import get_connection
from config import db_config


def get_community_names():
    connection = get_connection(db_config['social'])
    query = 'select distinct cp.community_name from social.communities_posts cp'
    return [res[0] for res in connection.execute(query)]


def get_community_image_urls(comm_name, start_time, stop_time):
    # TODO assert timestamps are strings
    connection = get_connection(db_config['social'])
    query = text('''select distinct l.url
        from social.links l
        join social.posts_links pl on pl.link_id=l.link_id
        join social.posts p on pl.post_id=p.post_id
        join social.communities_posts cp on cp.post_id=p.post_id 
        where l.type='image' 
        and cp.community_name = :comm_name
        and p.published_at >= :start_time 
        and p.published_at <= :stop_time;
        ''')
    print('query:', query)
    query_params = dict(comm_name=comm_name, start_time=start_time, stop_time=stop_time)
    return [res[0] for res in connection.execute(query, **query_params)]
