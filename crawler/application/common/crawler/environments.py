import os


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

    configs['driver_path'] = os.environ['DRIVER_PATH']

    # kafka info
    configs['kafka_hosts'] = [x for x in os.environ['KAFKA_HOSTS'].split()]

    # sua het cho nay
    configs['kafka_user'] = os.environ.get('KAFKA_USER', "default_value")
    configs['kafka_password'] = os.environ['KAFKA_PASSWORD']
    configs['kafka_num_partitions'] = int(os.environ['KAFKA_NUM_PARTITIONS'])
    configs['kafka_link_topic'] = os.environ['KAFKA_LINK_TOPIC']
    configs['kafka_consumer_group'] = os.environ['KAFKA_CONSUMER_GROUP']

    configs['redis_host'] = os.environ['REDIS_HOST']
    configs['redis_port'] = int(os.environ['REDIS_PORT'])
    configs['redis_db'] = os.environ['REDIS_DB']
    configs['redis_password'] = os.environ['REDIS_PASSWORD']

    configs['pg_host'] = os.environ['PG_HOST']
    configs['pg_port'] = int(os.environ['PG_PORT'])
    configs['pg_user'] = os.environ['PG_USER']
    configs['pg_password'] = os.environ['PG_PASSWORD']
    configs['pg_db'] = os.environ['PG_DB']

    # resume step
    configs['resume_step'] = int(os.environ['RESUME_STEP'])
    configs['restart_selenium_step'] = int(os.environ['RESTART_SELENIUM_STEP'])

    # external info
    configs['use_aws'] = bool(os.environ['USE_AWS'])
    configs['crawl_type'] = os.environ['CRAWL_TYPE']
    configs['download_images'] = bool(os.environ['DOWNLOAD_IMAGES'])

    return ConfigDict(configs)

