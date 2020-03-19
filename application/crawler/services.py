import sys
import json
import time
import base64
import requests
import application.crawler.scrapping as scrapping
from application.helpers.logger import get_logger
from application.crawler.model import DatabaseModel
from application.helpers.converter import optimize_dict
from application.crawler.environments import create_environments
from application.helpers.normalizer import JobNormalizer, CandidateNormalizer, BdsNormalizer

config = create_environments()
logger = get_logger('Service', logger_name=__name__)
sucess_link_log = get_logger('Success link', logger_name='success')


def _get_rules(redis_connect):
    return {
        _type: json.loads(redis_connect.get(_type + '_rules'))
        for _type in config.avaiable_crawl_type
    }, {
        _type: json.loads(redis_connect.get(_type + '_homes'))
        for _type in config.avaiable_crawl_type
    }


class UniversalExtractService:
    def __init__(self, _config, redis_connect, kafka_consumer, kafka_producer, db_connection=None):
        self.selenium_driver_path = _config.driver_path
        self.crawler_config = _config
        self.wrapSeleniumDriver = scrapping.WebDriverWrapper(self.selenium_driver_path)
        self.headless = True
        self.redis_connect = redis_connect
        self.url = None
        self.domain = None
        self.kafka_consumer = kafka_consumer
        self.kafka_producer = kafka_producer
        self.resume_step = _config.resume_step
        self.dict_rules, self.home_rules = _get_rules(redis_connect=self.redis_connect)
        self.normalizer = {
            'job': JobNormalizer(self.redis_connect),
            'candidate': CandidateNormalizer(self.redis_connect),
            'bds': BdsNormalizer(self.redis_connect),
        }
        if db_connection is None:
            raise ConnectionError

        self.db_connection = db_connection
        self.db_engine = _config.database_engine

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
    def create_pg_record_to_db(result):
        model = DatabaseModel()
        # if config.crawl_type == 'job':
        #     model.data = result
        #     model.currency_unit = result['currency_unit']
        #     model.title = result['title']
        #     model.salary = result['salary']
        #     model.salary_normalize = result['salary_normalize']
        #     model.url = result['url']
        #     model.company = result['company']
        #     model.location = result['location']
        #     model.info = result['info']
        #     model.degree_requirements = result['degree_requirements']
        #     model.deadline_submit = result['deadline_submit']
        #     model.experience = result['experience']
        #     model.no_of_opening = result['no_of_opening']
        #     model.formality = result['formality']
        #     model.position = result['position']
        #     model.gender_requirements = result['gender_requirements']
        #     model.career = result['career']
        #     model.description = result['description']
        #     model.benefit = result['benefit']
        #     model.job_requirements = result['job_requirements']
        #     model.profile_requirements = result['profile_requirements']
        #     model.contact = result['contact']
        #     model.other_info = result['other_info']
        # else:
        #     model.data = result
        model.data = result
        return model

    def send_link_to_kafka(self, _object):
        self.kafka_producer.send(
            self.crawler_config.crawl_type + '_' + self.crawler_config.kafka_object_topic, _object
        )
        time.sleep(0.01)

    def login(self, url_domain, _crawl_type):
        if self.home_rules[_crawl_type][url_domain]['login_require']:
            logger.info('Login into {}'.format(url_domain))
            try:
                if self.headless:
                    if self.wrapSeleniumDriver.driver is not None:
                        self.wrapSeleniumDriver.driver.close()
                    self.wrapSeleniumDriver = scrapping.WebDriverWrapper(
                        self.selenium_driver_path, headless=False
                    )
                    self.headless = False

                login_valid = self.wrapSeleniumDriver.driver.find_elements_by_css_selector(
                    self.home_rules[_crawl_type][url_domain]['valid_login']
                )
                if login_valid.__len__() == 0:
                    self.wrapSeleniumDriver.get_html(self.home_rules[_crawl_type][url_domain]['url_login'])
                    try:
                        if self.home_rules[_crawl_type][url_domain]['require_script'] is not None:
                            self.wrapSeleniumDriver.execute_script(
                                self.home_rules[_crawl_type][url_domain]['require_script']
                            )
                    except:
                        raise Exception("can't excute require script")

                    self.wrapSeleniumDriver.driver.execute_script(
                        "document.getElementsByName('{}')[0].value = '{}';".format(
                            self.home_rules[_crawl_type][url_domain]['input_username'],
                            self.home_rules[_crawl_type][url_domain]['username']
                        )
                    )
                    self.wrapSeleniumDriver.driver.execute_script(
                        "document.getElementsByName('{}')[0].value = '{}';".format(
                            self.home_rules[_crawl_type][url_domain]['input_password'],
                            self.home_rules[_crawl_type][url_domain]['password']
                        )
                    )

                    if 'script_submit' in self.home_rules[_crawl_type][url_domain]:
                        try:
                            self.wrapSeleniumDriver.execute_script(
                                self.home_rules[_crawl_type][url_domain]['script_submit']
                            )
                            time.sleep(2)
                        except Exception as ex:
                            raise Exception('Cant found login button: {}'.format(ex))
                    else:
                        for i in self.wrapSeleniumDriver.driver.find_elements_by_tag_name('input'):
                            if i.get_attribute('type') == 'submit':
                                i.click()
                                time.sleep(1)
                                break

            except Exception as ex:
                if self.wrapSeleniumDriver.driver is not None:
                    self.wrapSeleniumDriver.driver.close()
                self.wrapSeleniumDriver = scrapping.WebDriverWrapper(self.selenium_driver_path, headless=True)
                self.headless = True

                try:
                    _, _, lineno = sys.exc_info()
                    logger.error('Line error: {} - Error: {}'.format(lineno.tb_lineno, ex))
                except:
                    logger.error('Cannot get line error - Error {}'.format(ex))
                raise Exception('Login Exception ')

        else:
            if not self.headless:
                self.wrapSeleniumDriver.driver.close()
                self.wrapSeleniumDriver = scrapping.WebDriverWrapper(self.selenium_driver_path, headless=True)
                self.headless = True

    def scrape_page_streaming(self):
        logger.info("Start streaming")
        resume_step = 1

        for msg in self.kafka_consumer:
            try:
                resume_step += 1
                if resume_step % self.resume_step == 0:
                    logger.info("Restart rules")
                    self.dict_rules, _ = _get_rules(redis_connect=self.redis_connect)
                    resume_step = 0

                msg = msg.value

                if msg is None:
                    logger.info('Message from kafka is NULL >> SKIP')
                    continue

                url = msg['link']
                url_domain = url.split('/')[2]
                logger.info('Processing ' + str(url))

                if url_domain in config.ignore_list[msg['type']]:
                    logger.info('{} is in ignore list >> SKIP'.format(url_domain))
                    continue

                self.login(url_domain, msg['type'])
                self.set_page(url)

                if self.domain not in self.dict_rules[msg['type']]:
                    logger.info('Rule for {} is not exist >> SKIP'.format(self.domain))
                    continue

                if not self.get_page(url_domain, msg['type']):
                    logger.info('cannot get page >> SKIP')
                    continue

                if config.crawl_type == 'candidate' and url_domain == 'muaban.net':
                    try:
                        self.wrapSeleniumDriver.execute_script(
                            "document.querySelector('div.user-info__content div.mobile-container__value a').click();"
                        )
                    except Exception as ex:
                        logger.error(ex)

                # send rule
                dbfield = self.wrapSeleniumDriver.scrape_elements(rule=self.dict_rules[msg['type']][self.domain])

                if dbfield is None:
                    logger.info('Cannot get any field >> SKIP')
                    continue
                else:
                    result = self.extract_fields(dbfield)
                    result = optimize_dict(result)

                    # if sum([0 if result[key] is None else 1 for key in result]) / result.__len__() < 0.2:
                    #     logger.info('Too few field >> SKIP')
                    #     continue

                    result['source'] = url

                    if msg['type'] == 'job' and url_domain == 'careerbuilder.vn':
                        salary = self.wrapSeleniumDriver.driver.find_element_by_css_selector('ul.DetailJobNew')
                        result['salary'] = salary.find_elements_by_class_name('fl_right')[-2].text
                        # result['salary'] = salary.find_element_by_css_selector('label').text

                    # result['images'] = self.get_image(msg['type'])
                    result = self.normalizer[msg['type']].run_normalize(result)
                    if config.crawl_type == 'candidate':
                        if result['name'] == '' or result['salary_normalized'][0] > 400000000:
                            continue
                    elif config.crawl_type == 'bds':
                        result['id'] = int(str(time.time()).replace('.', ''))
                        result['source'] = url
                        result['domain'] = url_domain
                        self.send_link_to_kafka(result)

                    if self.db_engine == 'postgresql':
                        self.db_connection.insert_one(self.create_pg_record_to_db({'data': result}))
                    elif self.db_engine == 'mongodb':
                        self.db_connection[msg['type']].insert_one(result)

                    if config.crawl_type == 'candidate':
                        logger.info('Pushed \"{}\" to Database'.format(result['name']))
                    else:
                        logger.info('Pushed \"{}\" to Database'.format(result['title']))
                    sucess_link_log.info(url)

                self.clear_url_data()
            except Exception as ex:
                if self.wrapSeleniumDriver.driver is not None:
                    self.wrapSeleniumDriver.driver.close()
                self.wrapSeleniumDriver = scrapping.WebDriverWrapper(self.selenium_driver_path, headless=True)
                self.headless = True
                try:
                    _, _, lineno = sys.exc_info()
                    logger.error('Line error: {} - Error: {}'.format(lineno.tb_lineno, ex))
                except:
                    logger.error('Cannot get line error - Error{}'.format(ex))

    def get_page(self, _url_domain, _crawl_type):
        if not self.url:
            raise ConnectionAbortedError("Page does not exist!", self.url)

        try:
            self.wrapSeleniumDriver.use_selenium(self.home_rules[_crawl_type][_url_domain]['selenium'])
            self.wrapSeleniumDriver.get(self.url)
        except:
            return False
        return True

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
        self.url = None
        self.domain = None
