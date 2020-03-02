from application.helpers import logger
from psycopg2 import connect, extensions, errors
from kafka.errors import TopicAlreadyExistsError
from kafka.admin import KafkaAdminClient, NewTopic
from application.helpers.rule import push_all_yaml_to_redis
from application.crawler.environments import create_environments
from application.crawler.get_chromedriver import download_chrome_driver

config = create_environments()


def create_postgres_db(_config):
    logger.info_log.info("Create postgres database")
    connection = connect(
        host=_config.pg_host,
        port=_config.pg_port,
        user=_config.pg_user,
        password=_config.pg_password)

    connection.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    try:
        cursor.execute('CREATE DATABASE ' + _config.pg_db)
    except errors.DuplicateDatabase:
        logger.error_log.error('Database {} is exist, skip'.format(_config.pg_db))
    cursor.close()
    connection.close()
    logger.info_log.info('FINISH\n')


def create_kafka_topic(_config):
    if _config.kafka_user is None or _config.kafka_user == '':
        logger.info_log.info("Create kafka topic without sasl")
        admin_client = KafkaAdminClient(
            bootstrap_servers=_config.kafka_hosts,
            client_id=_config.kafka_user
        )
    else:
        logger.info_log.info("Create kafka topic with sasl")
        admin_client = KafkaAdminClient(
            bootstrap_servers=_config.kafka_hosts,
            client_id=_config.kafka_user,
            sasl_mechanism='PLAIN',
            sasl_plain_username=_config.kafka_user,
            sasl_plain_password=_config.kafka_password
        )

    topic_list = {
        _config.crawl_type + '_' + _config.kafka_link_topic: NewTopic(
            name=_config.crawl_type + '_' + _config.kafka_link_topic,
            num_partitions=_config.kafka_num_partitions,
            replication_factor=1
        ),
        _config.crawl_type + '_' + _config.kafka_object_topic: NewTopic(
            name=_config.crawl_type + '_' + _config.kafka_object_topic,
            num_partitions=_config.kafka_num_partitions,
            replication_factor=1
        )
    }

    for topic in topic_list:
        try:
            logger.info_log.info('Creating topic: {}'.format(topic))
            admin_client.create_topics(new_topics=[topic_list[topic]], validate_only=False)
        except TopicAlreadyExistsError:
            logger.error_log.error('Topic {} is exist --- skip'.format(topic))
            continue

    logger.info_log.info('FINISH\n')
    admin_client.close()


if __name__ == '__main__':
    create_kafka_topic(config)
    push_all_yaml_to_redis(config)
    create_postgres_db(config)
    download_chrome_driver()
