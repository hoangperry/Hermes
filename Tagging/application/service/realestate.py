import json

from application.common.helpers.url import UrlFormatter
from application.common.entity.realestate_normalizer import PropertyNormalizer
import application.common.crawler.scrapping as scrapping
from application.model.real_estate import Property
import application.common.content.text as text
from application.common.helpers.rule import RuleLoader
from kafka import KafkaConsumer, KafkaProducer

with open('config.json') as f:
    crawler_config = json.load(f)


class RealEstateExtractService:
    def __init__(self, selenium_driver, rule_dir):
        self.wrapSeleniumDriver = scrapping.WebDriverWrapper(selenium_driver)
        self.dict_rules = RuleLoader(rule_dir).load()
        self.url = None
        self.domain = None
        try:
            self.kafka_consumer_bsd_link = KafkaConsumer(crawler_config['consumer_receiver_topic'])
            self.kafka_producer_bsd_tagging = KafkaProducer(value_serializer=lambda v: json.dumps(v).encode('utf-8'))
        except Exception:
            raise Exception("Kafka service hasn't been started! ")

    def start_listening_data_link(self):
        print("RealEstateExtractService was started!!!")
        for msg in self.kafka_consumer_bsd_link:
            url = str(msg.value, "utf-8")
            self.set_page(url)
            dbfield = self.get_data_field()
            result = self.normalize_data(dbfield)
            self.kafka_producer_bsd_tagging.send(crawler_config['producer_sender_topic'], result)
            self.clear_url_data()

    def set_page(self, url):
        self.url = url
        self.domain = UrlFormatter(url=url).get_domain()

    def get_data_field(self):
        if not self.url:
            raise ConnectionAbortedError("Page is not exist!", self.url)

        rule = self.dict_rules[self.domain]
        self.wrapSeleniumDriver.get(self.url)
        return self.wrapSeleniumDriver.scrape_elements(rule=rule)

    def normalize_data(self, dbfield):
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
        :param dbfield: Array
        :return:
        """
        prop = Property(title=dbfield['title'],
                        price=dbfield['price'],
                        description=dbfield['description'],
                        total_area=dbfield['total_area'],
                        address=dbfield['address'],
                        contact_phone=dbfield['contact_phone'],
                        contact_name=dbfield['contact_name'],
                        source=self.url,
                        url_hash=text.encode(self.url, algorithm='md5'),
                        domain=UrlFormatter(url=self.url).get_domain(),
                        pre_direction=dbfield['pre_direction'],
                        pre_legal_status=dbfield['pre_legal_status'],
                        pre_location=dbfield['pre_location'],
                        pre_total_area=dbfield['pre_total_area'],
                        pre_total_area_width=dbfield['pre_total_area_width'],
                        pre_total_area_length=dbfield['pre_total_area_length'],
                        pre_construction_area=dbfield['pre_construction_area'],
                        pre_area_ilegal_recognized=dbfield['pre_area_ilegal_recognized'],
                        pre_floors=dbfield['pre_floors'],
                        pre_bedrooms=dbfield['pre_bedrooms'],
                        pre_bathrooms=dbfield['pre_bathrooms'],
                        pre_contact_name=dbfield['pre_contact_name'],
                        pre_contact_phone=dbfield['pre_contact_phone'],
                        pre_contact_address=dbfield['pre_contact_address'],
                        pre_contact_email=dbfield['pre_contact_email'],
                        contact_table=dbfield['contact_table'],
                        description_table=dbfield['description_table'])
        result = PropertyNormalizer(prop).normalize().__dict__
        return result

    def clear_url_data(self):
        self.url = None,
        self.domain = None
