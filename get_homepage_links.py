import redis
import kafka
from kafka import RoundRobinPartitioner, TopicPartition
from crawler.application.common.crawler.arguments import create_arguments
from crawler.application.common.crawler.environments import create_environments
from crawler.application.common.crawler.scrapping import WebDriverWrapper
from crawler.application.common.helpers import logger
from crawler.application.common.helpers.text import encode
import time
import json
from selenium.webdriver.support.ui import Select
import ssl
from crawler.application.common.helpers.thread import night_sleep


try:
    config = create_environments()
except Exception as ex:
    logger.error_log.error("Load config error")
    logger.error_log.error(str(ex))
    config = create_arguments()


def scrape_links(_config, sleep_per_step=20):
    # connect redis and kafka
    redis_connect = redis.StrictRedis(
        host=_config.redis_host,
        port=_config.redis_port,
        db=_config.redis_db,
        password=_config.redis_password
    )

    # create kafka partitions
    partitions = [
        TopicPartition(topic=_config.kafka_link_topic, partition=i) for i in range(0, _config.kafka_num_partitions)
    ]

    if _config.kafka_user is None:
        link_producer = kafka.KafkaProducer(
            bootstrap_servers=_config.kafka_hosts,
            partitioner=RoundRobinPartitioner(partitions=partitions),
            value_serializer=lambda x: json.dumps(
                x, indent=4, sort_keys=True, default=str, ensure_ascii=False
            ).encode('utf-8'),
            compression_type='gzip'
        )
    else:
        sasl_mechanism = 'PLAIN'
        security_protocol = 'SASL_PLAINTEXT'
        context = ssl.create_default_context()
        context.options &= ssl.OP_NO_TLSv1
        context.options &= ssl.OP_NO_TLSv1_1

        link_producer = kafka.KafkaProducer(
            bootstrap_servers=_config.kafka_hosts,
            partitioner=RoundRobinPartitioner(partitions=partitions),
            value_serializer=lambda x: json.dumps(
                x, indent=4, sort_keys=True, default=str, ensure_ascii=False
            ).encode('utf-8'),
            compression_type='gzip',
            sasl_plain_username=_config.kafka_user,
            sasl_plain_password=_config.kafka_password,
            security_protocol=security_protocol,
            ssl_context=context,
            sasl_mechanism=sasl_mechanism
        )

    while True:
        logger.info_log.info("Start/Restart selenium web browser")
        web_driver = WebDriverWrapper(_config.driver_path)
        web_driver.use_selenium(True)

        # get rule from redis by crawl type
        logger.info_log.info("Reload redis DB-0")
        rdh = redis_connect.get(_config.crawl_type + "_homes")
        homepage_rules = json.loads(rdh)

        # for home pages
        for hpg in homepage_rules.keys():
            rule = homepage_rules[hpg]
            for url in rule['start_urls']:

                logger.info_log.info("Process {}".format(url))

                web_driver.selenium = rule['selenium']
                # start
                web_driver.get(url, 5)

                if web_driver.driver is None:
                    continue

                if rule['start_script'] is not None:
                    web_driver.execute_script(rule['start_script'])

                if rule['select_element'] is not None:
                    select = Select(web_driver.driver.find_element_by_css_selector(rule['select_element']))
                    select.select_by_index(rule['select_value'])
                    time.sleep(1.5)
                    web_driver.set_html(web_driver.driver.page_source)

                # scrape, get all links
                links = web_driver.get_links()

                # add to redis and kafka
                for link in links:
                    hashed_link = encode(link)
                    if not redis_connect.exists(hashed_link):
                        logger.info_log.info("Add {} to kafka".format(link))
                        # add to redis and kafka
                        redis_connect.set(hashed_link, 0)
                        # send link in binary format
                        payload = {
                            'link': link,
                            'type': _config.crawl_type,
                        }
                        link_producer.send(_config.kafka_link_topic, payload)
                        time.sleep(0.01)

        # close browser and sleep
        web_driver.close_browser()

        # sleep
        night_sleep(other_case=sleep_per_step)


if __name__ == "__main__":
    try:
        # for i in range(0, config.num_threads):
        #     thr = threading.Thread(
        #         target=scrape_links,
        #         args=(config, 20)
        #     )
        #     thr.start()
        #     logger.info_log.info("Thread {} is successfully started".format(i))
        #     time.sleep(30)

        # we don't use multi-threads but replications instead
        scrape_links(config, 60)
    except Exception as ex:
        logger.error_log.error("Some thing went wrong. Application will stop after 1200 seconds")
        logger.error_log.exception(str(ex))
        time.sleep(1200)
