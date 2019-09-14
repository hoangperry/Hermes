import json


with open('config.json') as f:
    crawler_config = json.load(f)


class APIConfig:
    class RealEstateClassifier:
        headers = crawler_config['real_estate']['classifier_header']
        url = crawler_config['real_estate']['classifier_url']

    class PredictAddressFromText:
        headers = crawler_config['real_estate']['predict_address_header']
        url = crawler_config['real_estate']['predict_address_url']
        key = crawler_config['real_estate']['predict_address_key']


if __name__ == "__main__":
    conf = APIConfig
    print("HELLO WORLD")
