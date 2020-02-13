import requests
import json
import time
import os
import sys
import base64
from crawler.application.common.crawler.model import DatabaseModel
from crawler.application.common.helpers import logger
from crawler.application.common.helpers.converter import optimize_dict
from crawler.application.common.helpers.url import UrlFormatter
from crawler.application.common.crawler.environments import create_environments
from crawler.application.common.helpers.normalizer import normalize_job_crawler
import crawler.application.common.crawler.scrapping as scrapping

config = create_environments()


def _get_rules(redis_connect):
    return {
        _type: json.loads(redis_connect.get(str(_type) + '_rules'))
        for _type in config.avaiable_crawl_type
    }
    # return {
    #     'bds': json.loads(redis_connect.get('bds_rules')),
    #     'candidate': json.loads(redis_connect.get('candidate_rules')),
    #     'jobs': json.loads(redis_connect.get('jobs_rules')),
    # }


class UniversalExtractService:
    def __init__(self, selenium_driver_path, redis_connect,
                 kafka_consumer_bsd_link, kafka_object_producer,
                 object_topic, resume_step, crawl_type, restart_selenium_step,
                 download_images=False,
                 pg_connection=None):
        """

        :param selenium_driver:
        :param redis_connect:
        :param kafka_consumer_bsd_link:
        :param kafka_object_producer:
        :param object_topic:++
        :param resume_step:
        :param crawl_type:
        :param restart_selenium_step:
        :param download_images:
        :param pg_connection:
        """
        self.wrapSeleniumDriver = scrapping.WebDriverWrapper(selenium_driver_path)
        self.headless = True
        self.selenium_driver_path = selenium_driver_path
        self.redis_connect = redis_connect
        self.url = None
        self.domain = None
        self.kafka_consumer_bsd_link = kafka_consumer_bsd_link
        self.object_topic = object_topic
        self.kafka_object_producer = kafka_object_producer
        self.resume_step = resume_step
        self.crawl_type = crawl_type
        self.dict_rules = _get_rules(redis_connect=self.redis_connect)
        self.restart_selenium_step = restart_selenium_step
        self.download_images = download_images
        self.home_rules = json.loads(self.redis_connect.get(config.crawl_type + "_homes"))
        if pg_connection is None:
            raise ConnectionError

        self.pg_connection = pg_connection

    def set_page(self, url):
        self.url = url
        # self.domain = UrlFormatter(url=url).get_domain()
        self.domain = url.split("/")[2]
        self.domain = self.domain if self.domain.split('.')[0] != "www" else ".".join(self.domain.split('.')[1:])

    def get_image(self, _type_crawl):
        try:
            return [
                base64.b64encode(requests.get(i.get_attribute('src')).content)
                for i in
                self.wrapSeleniumDriver.driver.find_element_by_css_selector(
                    self.dict_rules[_type_crawl][self.domain]['image']
                ).find_elements_by_tag_name('img')
            ]
        except:
            return list()

    @staticmethod
    def create_record_to_db(result):
        model = DatabaseModel()
        if config.crawl_type == 'job':
            model.data = result
            model.currency_unit = result['currency_unit']
            model.salary = result['salary']
            model.salary_normalize = result['salary_normalize']
            model.url = result['url']
            model.company = result['company']
            model.location = result['location']
            model.info = result['info']
            model.degree_requirements = result['degree_requirements']
            model.deadline_submit = result['deadline_submit']
            model.experience = result['experience']
            model.no_of_opening = result['no_of_opening']
            model.formality = result['formality']
            model.position = result['position']
            model.gender_requirements = result['gender_requirements']
            model.career = result['career']
            model.description = result['description']
            model.benefit = result['benefit']
            model.job_requirements = result['job_requirements']
            model.profile_requirements = result['profile_requirements']
            model.contact = result['contact']
            model.other_info = result['other_info']
        else:
            model.data = result

        return model

    def scrape_page_streaming(self):
        logger.info_log.info("Start streaming")

        resume_step = 1

        for msg in self.kafka_consumer_bsd_link:
            try:
                resume_step += 1
                if resume_step % self.resume_step == 0:
                    logger.info_log.info("Restart rules")
                    self.dict_rules = _get_rules(redis_connect=self.redis_connect)
                    resume_step = 0

                msg = msg.value
                if msg is None:
                    pass
                url_domain = msg['link'].split('/')[2]
                # print(url_domain)

                if self.home_rules[url_domain]['login_require']:
                    try:
                        if self.headless:
                            self.wrapSeleniumDriver.driver.close()
                            self.wrapSeleniumDriver = scrapping.WebDriverWrapper(
                                self.selenium_driver_path, headless=False
                            )
                            self.headless = False

                        login_valid = self.wrapSeleniumDriver.driver.find_elements_by_css_selector(
                            self.home_rules[url_domain]['valid_login']
                        )
                        if login_valid.__len__() == 0:
                            self.wrapSeleniumDriver.get_html(self.home_rules[url_domain]['url_login'])

                            self.wrapSeleniumDriver.driver.execute_script(
                                "document.getElementsByName('{}')[0].value = '{}';".format(
                                    self.home_rules[url_domain]['input_username'],
                                    self.home_rules[url_domain]['username']
                                )
                            )
                            self.wrapSeleniumDriver.driver.execute_script(
                                "document.getElementsByName('{}')[0].value = '{}';".format(
                                    self.home_rules[url_domain]['input_password'],
                                    self.home_rules[url_domain]['password']
                                )
                            )
                            for i in self.wrapSeleniumDriver.driver.find_elements_by_tag_name('input'):
                                if i.get_attribute('type') == 'submit':
                                    i.click()
                                    time.sleep(1)
                                    break
                    except Exception as ex:
                        self.wrapSeleniumDriver.driver.close()
                        self.wrapSeleniumDriver = scrapping.WebDriverWrapper(self.selenium_driver_path, headless=True)
                        self.headless = True
                        logger.error_log('Login Exception ' + str(ex))
                        continue

                else:
                    if not self.headless:
                        self.wrapSeleniumDriver.driver.close()
                        self.wrapSeleniumDriver = scrapping.WebDriverWrapper(self.selenium_driver_path, headless=True)
                        self.headless = True

                url = msg['link']
                logger.info_log.info('Processing ' + str(url))
                try:
                    self.set_page(url)
                except Exception as ex:
                    exc_type, exc_obj, exc_tb = sys.exc_info()
                    fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                    logger.error_log.error(exc_type + ' | ' + fname + ' | ' + exc_tb.tb_lineno)
                    continue
                if self.domain not in self.dict_rules[msg['type']]:
                    continue
                rule = self.dict_rules[msg['type']][self.domain]
                # send rule
                dbfield = self.get_data_field(rule=rule)

                if dbfield is None:
                    continue
                else:
                    # result = self.normalize_data(dbfield)
                    result = self.extract_fields(dbfield)
                    result = optimize_dict(result)
                    if sum([0 if result[key] is None else 1 for key in result]) / result.__len__() < 0.2:
                        continue
                    # add url
                    result['url'] = url
                    # if extract, then send to another topic
                    # if self.object_topic is not None:
                    # self.kafka_object_producer.send(self.object_topic, result)

                    # get base64 image
                    if msg['type'] == 'job' and url_domain == 'careerbuilder.vn':
                        salary = self.wrapSeleniumDriver.driver.find_element_by_css_selector('ul.DetailJobNew')
                        salary = salary.find_elements_by_class_name('fl_right')[-2]
                        result['salary'] = salary.find_element_by_css_selector('label').text

                    result['images'] = self.get_image(msg['type'])
                    result['link'] = url
                    result = normalize_job_crawler(result)
                    # send to database
                    # model = DatabaseModel()
                    # model.data = result
                    # print(result)
                    self.pg_connection.insert_one(self.create_record_to_db(result))

                    logger.info_log.info('Pushed {} to Database'.format(result['title']))

                # clear url
                self.clear_url_data()
            except Exception as ex:
                self.wrapSeleniumDriver = scrapping.WebDriverWrapper(self.selenium_driver_path, headless=True)
                self.headless = True
                exc_type, exc_obj, exc_tb = sys.exc_info()
                fname = os.path.split(exc_tb.tb_frame.f_code.co_filename)[1]
                logger.error_log.error(exc_type + ' | ' + fname + ' | ' + exc_tb.tb_lineno)

    def get_data_field(self, rule):
        if not self.url:
            raise ConnectionAbortedError("Page is not exist!", self.url)

        # rule = self.dict_rules[self.domain]

        try:
            self.wrapSeleniumDriver.use_selenium(rule['selenium'])
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
