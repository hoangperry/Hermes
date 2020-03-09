import kafka
import json
import redis
from pyvirtualdisplay import Display
from application.helpers.logger import get_logger
from application.crawler.environments import create_environments
from application.crawler.model import DatabaseService
from application.crawler.services import UniversalExtractService
from pymongo import MongoClient

config = create_environments()
logger = get_logger('Scraper', logger_name=__name__)


if __name__ == "__main__":
    link_consumer = kafka.KafkaConsumer(
        config.crawl_type + '_' + config.kafka_link_topic,
        bootstrap_servers=config.kafka_hosts,
        value_deserializer=lambda x: json.loads(x.decode('utf-8')),
        group_id=config.kafka_consumer_group,
        auto_offset_reset='earliest',
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

    if config.database_engine == 'postgresql':
        db_service = DatabaseService(
            user=config.pg_user,
            password=config.pg_password,
            host=config.pg_host,
            port=config.pg_port,
            database=config.pg_db
        )
    elif config.database_engine == 'mongodb':
        client = MongoClient(
            config.mongodb_host,
            config.mongodb_port
        )
        client.admin.authenticate(
            config.mongodb_user,
            config.mongodb_password
        )
        db_service = client[config.mongodb_db]
    else:
        raise Exception("Invalid Database ENGINE ['mongodb'|'postgresql']")

    logger.info("Created postgresql service")
    # display = Display(visible=0, size=(800, 600))
    # display.start()
    logger.info("Created virtual display")
    while True:
        try:
            logger.info("Initial and Start Scraper")
            real_estate_scraper = UniversalExtractService(
                _config=config,
                redis_connect=redis_connect,
                kafka_consumer_bsd_link=link_consumer,
                db_connection=db_service,
            )
            real_estate_scraper.scrape_page_streaming()
        except Exception as ex:
            logger.error(ex)
