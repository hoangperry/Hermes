import os


DRIVER_PATH_DEFAULT = './chromedriver'
DEPLOY = 'local'

if DEPLOY == 'local':
    '''
    #####
    Variable Environment for multi-server deploy
    #####
    '''
    # Kafka default info
    KAFKA_HOSTS_DEFAULT = 'localhost:9092'
    KAFKA_USER_DEFAULT = None
    KAFKA_PASSWORD_DEFAULT = None
    KAFKA_NUM_PARTITIONS_DEFAULT = '50'
    KAFKA_LINK_TOPIC_DEFAULT = 'links_crawler'
    KAFKA_OBJECT_TOPIC_DEFAULT = 'object_crawler'
    KAFKA_CONSUMER_GROUP_DEFAULT = 'default'

    # Redis default info
    REDIS_HOST_DEFAULT = 'localhost'
    REDIS_PORT_DEFAULT = '6379'
    REDIS_DB_DEFAULT = '9'
    REDIS_PASSWORD_DEFAULT = ''

    # Postgre default info
    PG_HOST_DEFAULT = '34.87.189.111'
    PG_PORT_DEFAULT = '5432'
    PG_USER_DEFAULT = 'hoang'
    PG_PASSWORD_DEFAULT = '4983'
    PG_DB_DEFAULT = 'crawler'

    MONGODB_HOST_DEFAULT = '192.168.1.38'
    MONGODB_PORT_DEFAULT = '27017'
    MONGODB_USER_DEFAULT = 'hoang'
    MONGODB_PASSWORD_DEFAULT = '4983'
    MONGODB_DB_DEFAULT = 'crawler'

    # Other info
    DATABASE_ENGINE_DEFAULT = 'postgresql'
    RESUME_STEP_DEFAULT = '100'
    RESTART_SELENIUM_STEP_DEFAULT = '100'
    USE_AWS_DEFAULT = 'False'
    CRAWL_TYPE_DEFAULT = 'bds'
    DOWNLOAD_IMAGES_DEFAULT = 'True'
    YAML_FOLDER_DEFAULT = 'rules/'

elif DEPLOY == 'dps':
    '''
    #####
    Variable Environment for DPS deploy
    #####
    '''
    # Kafka default info
    KAFKA_HOSTS_DEFAULT = '35.186.148.118:9092'
    KAFKA_USER_DEFAULT = None
    KAFKA_PASSWORD_DEFAULT = None
    KAFKA_NUM_PARTITIONS_DEFAULT = '50'
    KAFKA_LINK_TOPIC_DEFAULT = 'links_job'
    KAFKA_OBJECT_TOPIC_DEFAULT = 'objects_job'
    KAFKA_CONSUMER_GROUP_DEFAULT = 'default'

    # Redis default info
    REDIS_HOST_DEFAULT = '192.168.1.89'
    REDIS_PORT_DEFAULT = '6381'
    REDIS_DB_DEFAULT = '0'
    REDIS_PASSWORD_DEFAULT = None

    # Postgre default info
    PG_HOST_DEFAULT = '35.186.148.118'
    PG_PORT_DEFAULT = '5432'
    PG_USER_DEFAULT = 'hoang'
    PG_PASSWORD_DEFAULT = '4983'
    PG_DB_DEFAULT = 'crawler_db'

    MONGODB_HOST_DEFAULT = 'localhost'
    MONGODB_PORT_DEFAULT = '27017'
    MONGODB_USER_DEFAULT = 'hoang'
    MONGODB_PASSWORD_DEFAULT = '4983'
    MONGODB_DB_DEFAULT = 'crawler'

    # Other info
    DATABASE_ENGINE_DEFAULT = 'postgresql'
    RESUME_STEP_DEFAULT = '100'
    RESTART_SELENIUM_STEP_DEFAULT = '100'
    USE_AWS_DEFAULT = 'False'
    CRAWL_TYPE_DEFAULT = 'candidate'
    DOWNLOAD_IMAGES_DEFAULT = 'True'
    YAML_FOLDER_DEFAULT = 'rules/'

elif DEPLOY == 'cloud':
    '''
    #####
    Variable Environment for cloud deploy
    #####
    '''
    # Kafka default info
    KAFKA_HOSTS_DEFAULT = '35.186.148.118:9092'
    KAFKA_USER_DEFAULT = None
    KAFKA_PASSWORD_DEFAULT = None
    KAFKA_NUM_PARTITIONS_DEFAULT = '50'
    KAFKA_LINK_TOPIC_DEFAULT = 'links_job'
    KAFKA_OBJECT_TOPIC_DEFAULT = 'objects_job'
    KAFKA_CONSUMER_GROUP_DEFAULT = 'default'

    # Redis default info
    REDIS_HOST_DEFAULT = '35.186.148.118'
    REDIS_PORT_DEFAULT = '6379'
    REDIS_DB_DEFAULT = '0'
    REDIS_PASSWORD_DEFAULT = None

    # Postgre default info
    PG_HOST_DEFAULT = '35.186.148.118'
    PG_PORT_DEFAULT = '5432'
    PG_USER_DEFAULT = 'hoang'
    PG_PASSWORD_DEFAULT = '4983'
    PG_DB_DEFAULT = 'dps_crawler'

    MONGODB_HOST_DEFAULT = 'localhost'
    MONGODB_PORT_DEFAULT = '27017'
    MONGODB_USER_DEFAULT = 'hoang'
    MONGODB_PASSWORD_DEFAULT = '4983'
    MONGODB_DB_DEFAULT = 'crawler'

    # Other info
    DATABASE_ENGINE_DEFAULT = 'postgresql'
    RESUME_STEP_DEFAULT = '100'
    RESTART_SELENIUM_STEP_DEFAULT = '100'
    USE_AWS_DEFAULT = 'False'
    CRAWL_TYPE_DEFAULT = 'bds'
    DOWNLOAD_IMAGES_DEFAULT = 'True'
    YAML_FOLDER_DEFAULT = 'rules/'


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
    configs['kafka_hosts'] = [x for x in os.environ.get('KAFKA_HOSTS', KAFKA_HOSTS_DEFAULT).split()]
    configs['kafka_user'] = os.environ.get('KAFKA_USER', KAFKA_USER_DEFAULT)
    configs['kafka_password'] = os.environ.get('KAFKA_PASSWORD', KAFKA_PASSWORD_DEFAULT)
    configs['kafka_num_partitions'] = int(os.environ.get('KAFKA_NUM_PARTITIONS', KAFKA_NUM_PARTITIONS_DEFAULT))
    configs['kafka_link_topic'] = os.environ.get('KAFKA_LINK_TOPIC', KAFKA_LINK_TOPIC_DEFAULT)
    configs['kafka_object_topic'] = os.environ.get('KAFKA_OBJECT_TOPIC', KAFKA_OBJECT_TOPIC_DEFAULT)
    configs['kafka_consumer_group'] = os.environ.get('KAFKA_CONSUMER_GROUP', KAFKA_CONSUMER_GROUP_DEFAULT)

    configs['redis_host'] = os.environ.get('REDIS_HOST', REDIS_HOST_DEFAULT)
    configs['redis_port'] = int(os.environ.get('REDIS_PORT', REDIS_PORT_DEFAULT))
    configs['redis_db'] = os.environ.get('REDIS_DB', REDIS_DB_DEFAULT)
    configs['redis_password'] = os.environ.get('REDIS_PASSWORD', REDIS_PASSWORD_DEFAULT)

    configs['pg_host'] = os.environ.get('PG_HOST', PG_HOST_DEFAULT)
    configs['pg_port'] = int(os.environ.get('PG_PORT', PG_PORT_DEFAULT))
    configs['pg_user'] = os.environ.get('PG_USER', PG_USER_DEFAULT)
    configs['pg_password'] = os.environ.get('PG_PASSWORD', PG_PASSWORD_DEFAULT)
    configs['pg_db'] = os.environ.get('PG_DB', PG_DB_DEFAULT)

    configs['mongodb_host'] = os.environ.get('MONGODB_HOST', MONGODB_HOST_DEFAULT)
    configs['mongodb_port'] = int(os.environ.get('MONGODB_PORT', MONGODB_PORT_DEFAULT))
    configs['mongodb_user'] = os.environ.get('MONGODB_USER', MONGODB_USER_DEFAULT)
    configs['mongodb_password'] = os.environ.get('MONGODB_PASSWORD', MONGODB_PASSWORD_DEFAULT)
    configs['mongodb_db'] = os.environ.get('MONGODB_DB', MONGODB_DB_DEFAULT)

    # resume step
    configs['database_engine'] = os.environ.get('DATABASE_ENGINE', DATABASE_ENGINE_DEFAULT)
    configs['resume_step'] = int(os.environ.get('RESUME_STEP', RESUME_STEP_DEFAULT))
    configs['restart_selenium_step'] = int(os.environ.get('RESTART_SELENIUM_STEP', RESTART_SELENIUM_STEP_DEFAULT))

    # external info
    configs['use_aws'] = bool(os.environ.get('USE_AWS', USE_AWS_DEFAULT))
    configs['crawl_type'] = os.environ.get('CRAWL_TYPE', CRAWL_TYPE_DEFAULT)
    configs['yaml_folder'] = os.environ.get('YAML_FOLDER', YAML_FOLDER_DEFAULT)
    configs['download_images'] = bool(os.environ.get('DOWNLOAD_IMAGES', DOWNLOAD_IMAGES_DEFAULT))

    configs['avaiable_crawl_type'] = [
        'bds',
        'candidate',
        'job',
    ]

    configs['ignore_list'] = {
        'candidate': [
            'facebook.com',
            'worklink.vn'
        ],
        'bds': [
            'facebook.com',
        ],
        'job': [
            'facebook.com',
        ],
    }

    return ConfigDict(configs)
