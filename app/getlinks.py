import redis
import kafka

from application.common.crawler.aruguments import config
from application.common.crawler.scrapping import WebDriverWrapper
from application.common.helpers import logger
from application.common.helpers.text import encode
from application.common.helpers.thread import real_estate_sleep
import time
import json
from selenium.webdriver.support.ui import Select


if __name__ == "__main__":

    # time.sleep(120)

    # connect redis and kafka
    redis_connect = redis.StrictRedis(
        host=config.redis_host,
        port=config.redis_port,
        db=config.redis_db,
        password=config.redis_password
    )

    link_producer = kafka.KafkaProducer(bootstrap_servers=config.kafka_host)

    while True:
        web_driver = WebDriverWrapper(config.driver_path)
        web_driver.use_selenium(True)

        # get rule from redis by crawl type
        rdh = redis_connect.get(config.crawl_type + "_homes")
        print("Load from redis")
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

                # scrape
                links = web_driver.get_links(rule['allow_pattern'])

                # add to redis and kafka
                for link in links:
                    hashed_link = encode(link)
                    if not redis_connect.exists(hashed_link):
                        logger.info_log.info("Add {} to kafka".format(link))
                        # add to redis and kafka
                        redis_connect.set(hashed_link, 0)
                        # send link in binary format
                        link_producer.send(config.kafka_link_topic, link.encode())
                        time.sleep(0.01)

        # close browser and sleep
        web_driver.close_browser()
        # sleep
        real_estate_sleep()
