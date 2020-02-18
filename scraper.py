import kafka
import json
import redis
from application.helpers.logger import get_logger
from application.crawler.environments import create_environments
from application.crawler.model import DatabaseService
from application.crawler.services import UniversalExtractService

config = create_environments()
logger = get_logger('Scraper', logger_name=__name__)

if __name__ == "__main__":
    link_consumer = kafka.KafkaConsumer(
        config.kafka_link_topic,
        bootstrap_servers=config.kafka_hosts,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        group_id=config.kafka_consumer_group
    )
    logger.info("Created kafka comsumer connection")

    object_producer = kafka.KafkaProducer(
        bootstrap_servers=config.kafka_hosts,
        value_serializer=lambda x: json.dumps(
            x, indent=4, sort_keys=True, default=str, ensure_ascii=False
        ).encode('utf-8')
    )
    logger.info("Created kafka producer connection")

    redis_connect = redis.StrictRedis(
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_db,
        password=config.redis_password
    )
    logger.info("Created redis connection")

    pg_service = DatabaseService(
        user=config.pg_user,
        password=config.pg_password,
        host=config.pg_host,
        port=config.pg_port,
        database=config.pg_db
    )
    logger.info("Created postgresql service")

    while True:
        try:
            real_estate_scraper = UniversalExtractService(
                selenium_driver_path=config.driver_path,
                redis_connect=redis_connect,
                kafka_consumer_bsd_link=link_consumer,
                kafka_object_producer=object_producer,
                object_topic=config.kafka_object_topic,
                resume_step=config.resume_step,
                crawl_type=config.crawl_type,
                restart_selenium_step=config.restart_selenium_step,
                download_images=config.download_images,
                pg_connection=pg_service
            )
            real_estate_scraper.scrape_page_streaming()
        except Exception as ex:
            print(ex)
