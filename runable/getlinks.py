import redis
import kafka
import argparse


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--rule_dir", required=True, help="Rules directory")
    args = parser.parse_args()

    redis_connect = redis.Redis()
    link_producer = kafka.KafkaConsumer()
    webdriver = None
