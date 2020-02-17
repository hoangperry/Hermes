import redis
import yaml
import os
import glob
import argparse
import json
from crawler.application.common.crawler.environments import create_environments


def push_all_yaml_to_redis(_config):
    redis_connect = redis.StrictRedis(
        host=config.redis_host, port=config.redis_port, db=config.redis_db, password=config.redis_password
    )
    all_data = dict()
    for _crawl_type in config.avaiable_crawl_type:
        for yaml_file in glob.glob(os.path.join(config.yaml_folder, _crawl_type, "pages/**.yaml")):
            with open(yaml_file, 'r') as stream:
                yaml_data = yaml.safe_load(stream)
                key = os.path.basename(os.path.splitext(yaml_file)[0])
                # if yaml_data is None:
                #     continue
                all_data[key] = yaml_data

        redis_connect.set(_crawl_type + "_rules", json.dumps(all_data))
        yaml_file = os.path.join(config.yaml_folder, _crawl_type, "homepages.yaml")

        with open(yaml_file, 'r') as stream:
            yaml_data = yaml.safe_load(stream)
            data = json.dumps(yaml_data)
            print(_crawl_type)
            redis_connect.set(_crawl_type + "_homes", data)
    redis_connect.close()


if __name__ == "__main__":
    config = create_environments()
