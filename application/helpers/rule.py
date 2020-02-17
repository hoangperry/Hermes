import yaml
import glob
import os
import redis
import json


def load_from_yaml(yaml_file):
    """
    Load all rules in directory
    All rules will be read by recursive walks
    :return: list of dictionary rules
    """
    with open(yaml_file, 'r') as stream:
        return yaml.safe_load(stream)


def load_from_db_config():
    raise NotImplementedError("This method will be implemented later")


def load_from_yaml_dir(directory):
    dict_rule = dict()
    for file in glob.glob(os.path.join(directory, "/**")):
        dict_rule[os.path.splitext(os.path.basename(file))[0]] = load_from_yaml(file)

    return dict_rule


def push_all_yaml_to_redis(_config):
    redis_connect = redis.StrictRedis(
        host=_config.redis_host,
        port=_config.redis_port,
        db=_config.redis_db,
        password=_config.redis_password
    )

    all_data = dict()
    for _crawl_type in _config.avaiable_crawl_type:
        for yaml_file in glob.glob(os.path.join(_config.yaml_folder, _crawl_type, "pages/**.yaml")):
            with open(yaml_file, 'r') as stream:
                yaml_data = yaml.safe_load(stream)
                key = os.path.basename(os.path.splitext(yaml_file)[0])
                if yaml_data is None:
                    continue
                all_data[key] = yaml_data

        redis_connect.set(_crawl_type + "_rules", json.dumps(all_data))
        yaml_file = os.path.join(_config.yaml_folder, _crawl_type, "homepages.yaml")

        with open(yaml_file, 'r') as stream:
            yaml_data = yaml.safe_load(stream)
            data = json.dumps(yaml_data)
            print(_crawl_type)
            redis_connect.set(_crawl_type + "_homes", data)

    redis_connect.close()
