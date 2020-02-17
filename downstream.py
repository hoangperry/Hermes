import kafka
import json
from application.crawler.environments import create_environments
from application.helpers import logger
import time

config = create_environments()


def insert(value):
    return value


if __name__ == "__main__":

    consumer = kafka.KafkaConsumer(
        bootstrap_servers=config.kafka_host,
        value_serializer=lambda x: json.dumps(
            x, indent=4, sort_keys=True, default=str
        ).encode('utf-8')
    )

    for message in consumer:
        # insert
        logger.info_log.info("Insert item")
        insert(message.value)
        time.sleep(0.01)
