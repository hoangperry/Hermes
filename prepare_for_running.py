from kafka.admin import KafkaAdminClient, NewTopic
from crawler.application.common.crawler.environments import create_environments
from yaml_to_redis import push_all_yaml_to_redis
from psycopg2 import connect, extensions

config = create_environments()


def create_postgres_db(_config):
    connection = connect(
        host=_config.pg_host,
        port=_config.pg_port,
        user=_config.pg_user,
        password=_config.pg_password)

    connection.set_isolation_level(extensions.ISOLATION_LEVEL_AUTOCOMMIT)
    cursor = connection.cursor()
    cursor.execute('CREATE DATABASE ' + _config.pg_db)
    cursor.close()
    connection.close()


def create_kafka_topic(_config):
    if _config.kafka_user is not None:
        admin_client = KafkaAdminClient(
            bootstrap_servers=_config.kafka_hosts,
            client_id=_config.kafka_user
        )
    else:
        admin_client = KafkaAdminClient(
            bootstrap_servers=_config.kafka_hosts,
            client_id=_config.kafka_user,
            sasl_mechanism='PLAIN',
            sasl_plain_username=_config.kafka_user,
            sasl_plain_password=_config.kafka_password
        )

    topic_list = [
        NewTopic(
            name=_config.kafka_link_topic,
            num_partitions=_config.kafka_num_partitions,
            replication_factor=1
        ),
        NewTopic(
            name=_config.kafka_object_topic,
            num_partitions=_config.kafka_num_partitions,
            replication_factor=1
        )
    ]

    admin_client.create_topics(new_topics=topic_list, validate_only=False)
    admin_client.close()


if __name__ == '__main__':
    create_kafka_topic(config)
    push_all_yaml_to_redis(config)
    create_postgres_db(config)
