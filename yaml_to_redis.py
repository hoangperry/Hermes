from application.crawler.environments import create_environments
from application.helpers.rule import push_all_yaml_to_redis


if __name__ == "__main__":
    config = create_environments()
    push_all_yaml_to_redis(config)
