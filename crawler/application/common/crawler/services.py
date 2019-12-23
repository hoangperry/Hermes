from application.common.crawler.model import DatabaseModel
from application.common.helpers import logger
from application.common.helpers.converter import optimize_dict
from application.common.helpers.url import UrlFormatter
import application.common.crawler.scrapping as scrapping
import json


def _get_rules(redis_connect, crawl_type):
    return json.loads(redis_connect.get(crawl_type))


class UniversalExtractService:
    def __init__(self, selenium_driver, redis_connect,
                 kafka_consumer_bsd_link, kafka_object_producer,
                 object_topic, resume_step, crawl_type, restart_selenium_step,
                 download_images=False,
                 pg_connection=None):
        """

        :param selenium_driver:
        :param redis_connect:
        :param kafka_consumer_bsd_link:
        :param kafka_object_producer:
        :param object_topic:
        :param resume_step:
        :param crawl_type:
        :param restart_selenium_step:
        :param download_images:
        :param pg_connection:
        """
        self.wrapSeleniumDriver = scrapping.WebDriverWrapper(selenium_driver)
        self.redis_connect = redis_connect
        self.url = None
        self.domain = None
        self.kafka_consumer_bsd_link = kafka_consumer_bsd_link
        self.object_topic = object_topic
        self.kafka_object_producer = kafka_object_producer
        self.resume_step = resume_step
        self.crawl_type = crawl_type
        self.dict_rules = _get_rules(redis_connect=self.redis_connect, crawl_type=self.crawl_type)
        self.restart_selenium_step = restart_selenium_step
        self.download_images = download_images

        if pg_connection is None:
            raise ConnectionError

        self.pg_connection = pg_connection

    def set_page(self, url):
        self.url = url
        self.domain = UrlFormatter(url=url).get_domain()

    def scrape_page_streaming(self):
        logger.info_log.info("Start streaming")

        resume_step = 1

        for msg in self.kafka_consumer_bsd_link:
            resume_step += 1
            if resume_step % self.resume_step == 0:
                logger.info_log.info("Restart rules")
                self.dict_rules = _get_rules(redis_connect=self.redis_connect, crawl_type=self.crawl_type)
                resume_step = 0

            msg = msg.value
            if msg is None:
                pass

            url = msg.decode("utf-8")

            try:
                self.set_page(url)
            except Exception as ex:
                logger.error_log.exception(str(ex))
                continue

            rule = self.dict_rules[self.domain]
            # send rule
            dbfield = self.get_data_field(rule=rule)

            if dbfield is None:
                continue
            else:
                # result = self.normalize_data(dbfield)
                result = self.extract_fields(dbfield)
                result = optimize_dict(result)

                # add url
                result['url'] = url
                # if extract, then send to another topic
                if self.object_topic is not None:
                    self.kafka_object_producer.send(self.object_topic, result)

                # send to database
                model = DatabaseModel()
                model.data = result

                self.pg_connection.insert_one(model)

            # clear url
            self.clear_url_data()

    def get_data_field(self, rule):
        if not self.url:
            raise ConnectionAbortedError("Page is not exist!", self.url)

        # rule = self.dict_rules[self.domain]
        self.wrapSeleniumDriver.use_selenium(rule['use_selenium'])
        try:
            self.wrapSeleniumDriver.get(self.url)
        except:
            return None

        return self.wrapSeleniumDriver.scrape_elements(rule=rule)

    @staticmethod
    def extract_fields(dbfields):
        table_prefixes = [x for x in dbfields.keys() if x.startswith("pre_")]

        for key, value in dbfields.items():
            if value is not None and len(value) > 0:
                if key.endswith("_table"):
                    for prefix in table_prefixes:
                        dbfields[prefix.replace("pre_", "")] = value[0]
                else:
                    dbfields[key] = value[0]

        return dbfields

    def clear_url_data(self):
        self.url = None,
        self.domain = None
