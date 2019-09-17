import argparse
import kafka
import json
from application.service.realestate import RealEstateExtractService

if __name__ == "__main__":

    # time.sleep(60)

    parser = argparse.ArgumentParser()
    parser.add_argument("--driver_path", required=False, help="Rules directory", default='/usr/bin/chromedriver')
    parser.add_argument("--rule_dir", required=False, help="Rules directory", default='rules/realestate/')
    parser.add_argument("--link_topic", required=False, help="Rules directory", default="links")
    parser.add_argument("--object_topic", required=False, help="Rules directory", default="objects")

    args = parser.parse_args()

    # link consumer
    link_consumer = kafka.KafkaConsumer()
    link_consumer.subscribe([args.link_topic])

    # and object producer for another process
    object_producer = kafka.KafkaProducer(value_serializer=lambda x: json.dumps(x, indent=4, sort_keys=True, default=str).encode('utf-8'))

    # create webdriver
    real_estate_scraper = RealEstateExtractService(
        selenium_driver=args.driver_path,
        rule_dir=args.rule_dir,
        kafka_consumer_bsd_link=link_consumer,
        kafka_object_producer=object_producer,
        object_topic=args.object_topic
    )

    real_estate_scraper.scrape_page_streaming()
