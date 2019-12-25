import redis
import yaml
import os
import glob
import argparse
import json


if __name__ == "__main__":
    parser = argparse.ArgumentParser()

    parser.add_argument("--host", required=False, help="Redis server", default="localhost")
    parser.add_argument("--port", required=False, help="Redis port", default=6379)
    parser.add_argument("--db", required=False, help="Redis database number", default=1)
    parser.add_argument("--password", required=False, help="Redis authentication password", default=None)

    parser.add_argument("--yaml_folder", required=False, default="rules/bds/")
    parser.add_argument("--type", required=False, default="bds")

    args = parser.parse_args()

    redis_connect = redis.StrictRedis(host=args.host, port=args.port, db=args.db, password=args.password)

    all_data = dict()
    for yaml_file in glob.glob(os.path.join(args.yaml_folder, "pages/**.yaml")):
        with open(yaml_file, 'r') as stream:
            yaml_data = yaml.safe_load(stream)
            key = os.path.basename(os.path.splitext(yaml_file)[0])
            # if yaml_data is None:
            #     continue
            all_data[key] = yaml_data

    redis_connect.set(args.type + "_rules", json.dumps(all_data))

    yaml_file = os.path.join(args.yaml_folder, "homepages.yaml")

    with open(yaml_file, 'r') as stream:
        yaml_data = yaml.safe_load(stream)
        data = json.dumps(yaml_data)
        print(args.type)
        redis_connect.set(args.type + "_homes", data)
