import argparse
import sys
import os

from application.common.helpers import logger


def create_arguments(name=sys.argv[0], args=sys.argv[1:]):
    """
    Create argument based on file name and args
    :param name:
    :param args:
    :return:
    """
    parser = argparse.ArgumentParser()

    parser.add_argument("--driver_path", required=False, help="Selenium driver path", default='/usr/bin/chromedriver')
    parser.add_argument("--kafka_host", required=True, help="Kafka host")
    # redis server info
    # this server is using to stored rule
    # all rules can be modified in admin dashboard
    parser.add_argument("--redis_host", required=True, help="Redis server")
    parser.add_argument("--redis_port", required=False, help="Redis port", default=6379)
    parser.add_argument("--redis_db", required=False, help="Redis database number", default=1)
    parser.add_argument("--redis_password", required=False, help="Redis authentication password", default=None)
    parser.add_argument("--kafka_link_topic", required=False, help="Rules directory", default="links")

    # crawling type
    # this option using for limit web pages
    parser.add_argument("--crawl_type", required=True, help="Limit web pages")

    if name == os.path.join(os.getcwd(), 'extractor.py'):
        logger.info_log.info("Starting get web content")
        parser.add_argument("--object_topic",
                            required=False,
                            help="Kafka object topic. This topic is using for extract",
                            default="objects")

        # add feature
        parser.add_argument("--kafka_consumer_group", required=True, help="Consumer group id")
        parser.add_argument("--resume_step", required=False, default=10000)
        parser.add_argument("--restart_selenium_step", required=False, default=500)

        # download images
        parser.add_argument("--download_images", required=False, default=False)

        # data warehouse
        parser.add_argument("--pg_host", required=True)
        parser.add_argument("--pg_port", required=False, default=5432)
        parser.add_argument("--pg_user", required=True)
        parser.add_argument("--pg_password", required=True)
        parser.add_argument("--pg_db", required=False, default="crawled")
        parser.add_argument("--pg_relation", required=True)
    else:
        logger.info_log.info("Starting get links")

    options = parser.parse_args(args)
    return options


config = create_arguments()
