import os


DRIVER_PATH_DEFAULT = '/usr/local/bin/chromedriver'
DEPLOY = 'local'

# Kafka default info
LOCAL_KAFKA_HOSTS_DEFAULT = 'localhost:9092'
LOCAL_KAFKA_USER_DEFAULT = None
LOCAL_KAFKA_PASSWORD_DEFAULT = None
LOCAL_KAFKA_NUM_PARTITIONS_DEFAULT = '10'
LOCAL_KAFKA_LINK_TOPIC_DEFAULT = 'links'
LOCAL_KAFKA_OBJECT_TOPIC_DEFAULT = 'objects'
LOCAL_KAFKA_CONSUMER_GROUP_DEFAULT = 'default'

# Redis default info
LOCAL_REDIS_HOST_DEFAULT = 'localhost'
LOCAL_REDIS_PORT_DEFAULT = '6379'
LOCAL_REDIS_DB_DEFAULT = '9'
LOCAL_REDIS_PASSWORD_DEFAULT = None

# Postgre default info
LOCAL_PG_HOST_DEFAULT = 'localhost'
LOCAL_PG_PORT_DEFAULT = '5432'
LOCAL_PG_USER_DEFAULT = 'hoang'
LOCAL_PG_PASSWORD_DEFAULT = '4983'
LOCAL_PG_DB_DEFAULT = 'test_crawler'

# Other info
LOCAL_RESUME_STEP_DEFAULT = '100'
LOCAL_RESTART_SELENIUM_STEP_DEFAULT = '100'
LOCAL_USE_AWS_DEFAULT = 'False'
LOCAL_CRAWL_TYPE_DEFAULT = 'job'
LOCAL_DOWNLOAD_IMAGES_DEFAULT = 'True'
LOCAL_DEEP_CRAWL_DEFAULT = 'True'
LOCAL_YAML_FOLDER_DEFAULT = 'rules/'


class ConfigDict(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__
    __delattr__ = dict.__delitem__


def create_environments():
    """
    Create argument based on file name and environment variables
    :return:
    """

    configs = dict()

    configs['driver_path'] = os.environ.get('DRIVER_PATH', DRIVER_PATH_DEFAULT)

    # kafka info
    configs['kafka_hosts'] = [x for x in os.environ.get('KAFKA_HOSTS', LOCAL_KAFKA_HOSTS_DEFAULT).split()]

    configs['kafka_user'] = os.environ.get('KAFKA_USER', LOCAL_KAFKA_USER_DEFAULT)
    configs['kafka_password'] = os.environ.get('KAFKA_PASSWORD', LOCAL_KAFKA_PASSWORD_DEFAULT)
    configs['kafka_num_partitions'] = int(os.environ.get('KAFKA_NUM_PARTITIONS', LOCAL_KAFKA_NUM_PARTITIONS_DEFAULT))
    configs['kafka_link_topic'] = os.environ.get('KAFKA_LINK_TOPIC', LOCAL_KAFKA_LINK_TOPIC_DEFAULT)
    configs['kafka_object_topic'] = os.environ.get('KAFKA_OBJECT_TOPIC', LOCAL_KAFKA_OBJECT_TOPIC_DEFAULT)
    configs['kafka_consumer_group'] = os.environ.get('KAFKA_CONSUMER_GROUP', LOCAL_KAFKA_CONSUMER_GROUP_DEFAULT)

    configs['redis_host'] = os.environ.get('REDIS_HOST', LOCAL_REDIS_HOST_DEFAULT)
    configs['redis_port'] = int(os.environ.get('REDIS_PORT', LOCAL_REDIS_PORT_DEFAULT))
    configs['redis_db'] = os.environ.get('REDIS_DB', LOCAL_REDIS_DB_DEFAULT)
    configs['redis_password'] = os.environ.get('REDIS_PASSWORD', LOCAL_REDIS_PASSWORD_DEFAULT)

    configs['pg_host'] = os.environ.get('PG_HOST', LOCAL_PG_HOST_DEFAULT)
    configs['pg_port'] = int(os.environ.get('PG_PORT', LOCAL_PG_PORT_DEFAULT))
    configs['pg_user'] = os.environ.get('PG_USER', LOCAL_PG_USER_DEFAULT)
    configs['pg_password'] = os.environ.get('PG_PASSWORD', LOCAL_PG_PASSWORD_DEFAULT)
    configs['pg_db'] = os.environ.get('PG_DB', LOCAL_PG_DB_DEFAULT)

    # resume step
    configs['resume_step'] = int(os.environ.get('RESUME_STEP', LOCAL_RESUME_STEP_DEFAULT))
    configs['restart_selenium_step'] = int(os.environ.get('RESTART_SELENIUM_STEP', LOCAL_RESTART_SELENIUM_STEP_DEFAULT))

    # external info
    configs['use_aws'] = bool(os.environ.get('USE_AWS', LOCAL_USE_AWS_DEFAULT))
    configs['crawl_type'] = os.environ.get('CRAWL_TYPE', LOCAL_CRAWL_TYPE_DEFAULT)
    configs['yaml_folder'] = os.environ.get('YAML_FOLDER', LOCAL_YAML_FOLDER_DEFAULT)
    configs['download_images'] = bool(os.environ.get('DOWNLOAD_IMAGES', LOCAL_DOWNLOAD_IMAGES_DEFAULT))
    configs['deep_crawl'] = bool(os.environ.get('DEEP_CRAWL', LOCAL_DEEP_CRAWL_DEFAULT))

    configs['avaiable_crawl_type'] = [
        'bds',
        'candidate',
        'job',
    ]
    return ConfigDict(configs)
