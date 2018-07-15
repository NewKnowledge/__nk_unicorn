import os

SOCIAL_DB_HOST = os.getenv('SOCIAL_DB_HOST', 'social-db')
SOCIAL_DB_NAME = os.getenv('SOCIAL_DB_NAME', 'social')
SOCIAL_DB_USER = os.getenv('SOCIAL_DB_USER', 'social')
SOCIAL_DB_PASS = os.getenv('SOCIAL_DB_PASS', '')

CLUSTER_DB_HOST = os.getenv('CLUSTER_DB_HOST', 'cluster-db')
CLUSTER_DB_NAME = os.getenv('CLUSTER_DB_NAME', 'cluster')
CLUSTER_DB_USER = os.getenv('CLUSTER_DB_USER', 'cluster')
CLUSTER_DB_PASS = os.getenv('CLUSTER_DB_PASS', '')

API_PASSWORD = os.getenv('API_PASSWORD', 'pizza')

CACHE_TTL = os.getenv('CACHE_TTL', 3600)  # time to live for cache in seconds

DB_CONFIG = {
    'cluster': {
        'host': CLUSTER_DB_HOST,
        'db_name': CLUSTER_DB_NAME,
        'user': CLUSTER_DB_USER,
        'password': CLUSTER_DB_PASS
    },
    'social': {
        'host': SOCIAL_DB_HOST,
        'db_name': SOCIAL_DB_NAME,
        'user': SOCIAL_DB_USER,
        'password': SOCIAL_DB_PASS
    }
}
