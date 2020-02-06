import redis
import kafka
import time
import json
import ssl
import re
from kafka import RoundRobinPartitioner
from crawler.application.common.crawler.environments import create_environments
from crawler.application.common.crawler.scrapping import WebDriverWrapper
from crawler.application.common.helpers import logger
from crawler.application.common.helpers.text import encode
from selenium.webdriver.support.ui import Select
from crawler.application.common.helpers.thread import night_sleep


config = create_environments()


class LinkScraper:

    def __init__(self, _config, sleep_per_step=5):
        self.config = config
        self.redis_connect = self.create_redis_connection()
        self.link_producer = self.create_kafka_producer()
        self.sleep_per_step = sleep_per_step

    def create_redis_connection(self):
        return redis.StrictRedis(
            host=self.config.redis_host,
            port=self.config.redis_port,
            db=self.config.redis_db,
            password=self.config.redis_password
        )

    def create_kafka_producer(self):
        partitions = [
            kafka.TopicPartition(
                topic=self.config.kafka_link_topic, partition=i
            ) for i in range(0, self.config.kafka_num_partitions)
        ]

        if self.config.kafka_user is None:
            return kafka.KafkaProducer(
                bootstrap_servers=self.config.kafka_hosts,
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

            return kafka.KafkaProducer(
                bootstrap_servers=self.config.kafka_hosts,
                partitioner=RoundRobinPartitioner(partitions=partitions),
                compression_type='gzip',
                value_serializer=lambda x: json.dumps(
                    x, indent=4, sort_keys=True, default=str, ensure_ascii=False
                ).encode('utf-8'),
                sasl_plain_username=self.config.kafka_user,
                sasl_plain_password=self.config.kafka_password,
                security_protocol=security_protocol,
                ssl_context=context,
                sasl_mechanism=sasl_mechanism
            )

    def run(self):
        while True:
            logger.info_log.info("Start/Restart selenium web browser")
            web_driver = WebDriverWrapper(self.config.driver_path)
            web_driver.use_selenium(True)

            # get rule from redis by crawl type
            logger.info_log.info("Load from redis")
            homepage_rules = json.loads(self.redis_connect.get(self.config.crawl_type + "_homes"))

            # for home pages
            for hpg in homepage_rules.keys():
                homepage_rules = json.loads(self.redis_connect.get(self.config.crawl_type + "_homes"))
                count_loop = 0
                rule = homepage_rules[hpg]
                rule['start_urls'] = [rule['homepage']] + rule['start_urls']
                new_start_urls = rule['start_urls'].copy()
                for url in rule['start_urls']:
                    count_loop += 1

                    if count_loop > 5:
                        break

                    new_start_urls.remove(url)

                    logger.info_log.info("Process {}".format(url))
                    web_driver.selenium = rule['selenium']
                    # start
                    if url.split('/')[2] != hpg:
                        rule['start_urls'] = new_start_urls
                        self.redis_connect.set(self.config.crawl_type + "_homes", json.dumps(homepage_rules))
                        continue

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
                        if link.split('/')[2] != hpg:
                            continue
                        hashed_link = encode(link)
                        if not self.redis_connect.exists(hashed_link):
                            new_start_urls.append(link)
                            if not re.match(rule['allow_pattern'], link):
                                # if _config.deep_crawl:
                                continue
                            # new_start_urls.append(link)
                            logger.info_log.info("Add {} to kafka".format(link))
                            # add to redis and kafka
                            self.redis_connect.set(hashed_link, 0)
                            # send link in binary format
                            payload = {
                                'link': link,
                                'type': self.config.crawl_type,
                            }
                            self.link_producer.send(self.config.kafka_link_topic, payload)
                            time.sleep(0.01)

                rule['start_urls'] = new_start_urls
                self.redis_connect.set(self.config.crawl_type + "_homes", json.dumps(homepage_rules))

            # close browser and sleep
            web_driver.close_browser()
            # sleep
            night_sleep(other_case=self.sleep_per_step)
            

if __name__ == "__main__":
    try:
        link_scraper = LinkScraper(config, sleep_per_step=5)
        link_scraper.run()
    except Exception as ex:
        logger.error_log.error("Some thing went wrong. Application will stop after 1200 seconds")
        logger.error_log.exception(str(ex))
        time.sleep(1)
