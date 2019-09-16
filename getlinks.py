import redis
import kafka
import argparse
import application.config.api_config as config
from application.common.crawler.scrapping import WebDriverWrapper
from application.common.helpers import logger
from application.common.helpers.text import encode
from application.common.helpers.thread import real_estate_sleep
import time
from selenium.webdriver.support.ui import Select



if __name__ == "__main__":

    # time.sleep(120)

    parser = argparse.ArgumentParser()
    parser.add_argument("--driver_path", required=False, help="Rules directory", default='/usr/bin/chromedriver')
    parser.add_argument("--link_topic", required=False, help="Rules directory", default="links")

    args = parser.parse_args()

    redis_connect = redis.Redis()
    link_producer = kafka.KafkaProducer()
    webdriver = WebDriverWrapper(args.driver_path)
    webdriver.use_selenium(True)

    while True:
        # for home pages
        for homepage, values in config.homepages.items():
            for url in values['start_urls']:

                logger.info_log.info("Process {}".format(url))

                # start
                webdriver.get(url, 5)

                if values['start_script'] is not None:
                    webdriver.execute_script(values['start_script'])

                if values['select_element'] is not None:
                    select = Select(webdriver.driver.find_element_by_css_selector(values['select_element']))
                    select.select_by_index(values['select_value'])
                    time.sleep(1.5)
                    webdriver.set_html(webdriver.driver.page_source)

                # scrape
                links = webdriver.get_links(values['allow_pattern'])

                # add to redis and kafka
                for link in links:
                    hashed_link = encode(link)
                    if not redis_connect.exists(hashed_link):
                        logger.info_log.info("Add {} to kafka".format(link))
                        # add to redis and kafka
                        redis_connect.set(hashed_link, 0)
                        enc_link = link.encode()
                        link_producer.send(args.link_topic, enc_link)
                        time.sleep(0.01)
        # sleep
        real_estate_sleep()
