import kafka
import json
import redis

from crawler.application.common.crawler.environments import create_environments
from crawler.application.common.crawler.model import DatabaseService
from crawler.application.common.crawler.services import UniversalExtractService

config = create_environments()


if __name__ == "__main__":

    # time.sleep(60)

    # connect kafka and create consumers
    # link consumer
    link_consumer = kafka.KafkaConsumer(config.kafka_link_topic,
                                        bootstrap_servers=config.kafka_hosts,
                                        group_id=config.kafka_consumer_group)
    link_consumer.subscribe([config.kafka_link_topic])
    # and object producer for another process
    object_producer = kafka.KafkaProducer(bootstrap_servers=config.kafka_hosts,
                                          value_serializer=lambda x: json.dumps(x, indent=4, sort_keys=True, default=str).encode('utf-8'))

    # connect redis
    # load rule from path
    redis_connect = redis.StrictRedis(
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_db,
        password=config.redis_password
    )

    # connect postgresql
    pg_service = DatabaseService(
        user=config.pg_user,
        password=config.pg_password,
        host=config.pg_host,
        port=config.pg_port,
        database=config.pg_db
    )

    # create webdriver
    real_estate_scraper = UniversalExtractService(
        selenium_driver=config.driver_path,
        redis_connect=redis_connect,
        kafka_consumer_bsd_link=link_consumer,
        kafka_object_producer=object_producer,
        object_topic=config.kafka_link_topic,
        resume_step=config.resume_step,
        crawl_type=config.crawl_type,
        restart_selenium_step=config.restart_selenium_step,
        download_images=config.download_images,
        pg_connection=pg_service
    )

    real_estate_scraper.scrape_page_streaming()
