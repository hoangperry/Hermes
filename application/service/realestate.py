import datetime
import json

from application.common.helpers import logger
from application.common.helpers.url import UrlFormatter
from application.common.entity.realestate_normalizer import PropertyNormalizer
import application.common.crawler.scrapping as scrapping
from application.model.real_estate import Property
from application.common.helpers.rule import RuleLoader

with open('config.json') as f:
    crawler_config = json.load(f)


class RealEstateExtractService:
    def __init__(self, selenium_driver, rule_dir, kafka_consumer_bsd_link, kafka_object_producer, object_topic):
        self.wrapSeleniumDriver = scrapping.WebDriverWrapper(selenium_driver)
        self.dict_rules = RuleLoader(rule_dir).load()
        self.url = None
        self.domain = None
        self.kafka_consumer_bsd_link = kafka_consumer_bsd_link
        self.object_topic = object_topic
        self.kafka_object_producer = kafka_object_producer

    def start_listening_data_link(self):
        print("RealEstateExtractService was started!!!")
        for msg in self.kafka_consumer_bsd_link:
            url = str(msg.value, "utf-8")
            self.set_page(url)
            dbfield = self.get_data_field()
            result = self.normalize_data(dbfield)
            self.kafka_object_producer.send(crawler_config['producer_sender_topic'], result)
            self.clear_url_data()

    def set_page(self, url):
        self.url = url
        self.domain = UrlFormatter(url=url).get_domain()

    def scrape_page_streaming(self):
        logger.info_log.info("Start streaming")
        for msg in self.kafka_consumer_bsd_link:
            url = str(msg.value, "utf-8")
            # logger.info_log.info("Scrape {}".format(url))
            self.set_page(url)
            dbfield = self.get_data_field()
            result = self.normalize_data(dbfield)
            result = result.optimize_dict()
            # result_dict = result.__dict__
            self.kafka_object_producer.send(self.object_topic, result)
            self.clear_url_data()

    def get_data_field(self):
        if not self.url:
            raise ConnectionAbortedError("Page is not exist!", self.url)

        rule = self.dict_rules[self.domain]
        self.wrapSeleniumDriver.use_selenium(rule['use_selenium'])
        self.wrapSeleniumDriver.get(self.url)
        return self.wrapSeleniumDriver.scrape_elements(rule=rule)

    def normalize_data(self, result):
        """
        Example dictionary
            'domain' (140719183137008) = {str} 'alonhadat.com.vn'
            'allow_pattern' (140719183128816) = {str} '.*\\d+\\.html$'
            'use_selenium' (140719183128752) = {bool} False
            'title' (140719183136448) = {str} 'h1'
            'posted_date' (140719183128624) = {str} 'span.date'
            'description' (140719183128368) = {str} 'div.detail'
            'price' (140719183137120) = {str} 'span.price'
            'address' (140719183136560) = {str} 'div.address > span.value'
            'total_area' (140719183128560) = {str} 'span.square > span.value'
            'description_table' (140719183117024) = {str} 'div.infor > table > tbody > tr'
            'contact_table' (140719183128304) = {str} 'null'
            'pre_direction' (140719183128176) = {str} 'Hướng'
            'pre_legal_status' (140719183116592) = {str} 'Pháp lý'
            'pre_location' (140719183128112) = {str} 'null'
            'pre_total_area' (140719183128240) = {str} 'null'
            'pre_total_area_width' (140719183116664) = {str} 'Chiều ngang'
            'pre_total_area_length' (140719183117528) = {str} 'Chiều dài'
            'pre_construction_area' (140719183116736) = {str} 'null'
            'pre_area_ilegal_recognized' (140719182659632) = {str} 'null'
            'pre_floors' (140719183127984) = {str} 'Số lầu'
            'pre_bedrooms' (140719183128048) = {str} 'Số phòng ngủ'
            'pre_bathrooms' (140719183127920) = {str} 'null'
            'pre_contact_name' (140719183116880) = {str} 'null'
            'pre_contact_phone' (140719183116808) = {str} 'null'
            'pre_contact_address' (140719183116952) = {str} 'null'
            'pre_contact_email' (140719182667824) = {str} 'null'
            'contact_name' (140719183127728) = {str} 'div.content > div.name'
            'contact_phone' (140719183127856) = {str} 'div.content > div.fone'
            'contact_email' (140719183130288) = {str} 'null'
        :param result: Array
        :return:
        """
        prop = Property()
        prop.set_dict(title=result['title'],
                      price=result['price'],
                      description=result['description'],
                      total_area=result['total_area'],
                      address=result['address'],
                      contact_phone=result['contact_phone'],
                      contact_name=result['contact_name'],
                      source=self.url,
                      domain=self.domain,
                      updated_date=datetime.datetime.now(),
                      pre_direction=result['pre_direction'],
                      pre_legal_status=result['pre_legal_status'],
                      pre_location=result['pre_location'],
                      pre_total_area=result['pre_total_area'],
                      pre_total_area_width=result['pre_total_area_width'],
                      pre_total_area_length=result['pre_total_area_length'],
                      pre_construction_area=result['pre_construction_area'],
                      pre_area_ilegal_recognized=result['pre_area_ilegal_recognized'],
                      pre_floors=result['pre_floors'],
                      pre_bedrooms=result['pre_bedrooms'],
                      pre_bathrooms=result['pre_bathrooms'],
                      pre_contact_name=result['pre_contact_name'],
                      pre_contact_phone=result['pre_contact_phone'],
                      pre_contact_address=result['pre_contact_address'],
                      pre_contact_email=result['pre_contact_email'],
                      contact_table=result['contact_table'],
                      description_table=result['description_table'],
                      pre_property_address=result['pre_property_address'] if "pre_property_address" in result else None)

        prop = PropertyNormalizer(prop).normalize()
        return prop

    def clear_url_data(self):
        self.url = None,
        self.domain = None
