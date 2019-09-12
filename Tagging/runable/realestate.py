import threading
from application.service.realestate import RealEstateExtractService


def run_selenium(rule_dir, selenium_driver):
    print("Create selenium thread...")
    # CrawlerConfiguration.set_config(proxy_file=proxy_file)

    RealEstateExtractService(selenium_driver=selenium_driver, rule_dir=rule_dir).start_listening_data_link()


def run(proxy_file, rule_dir, selenium_driver):
    thread_1 = threading.Thread(target=run_selenium,
                                args=[rule_dir, selenium_driver])

    thread_1.start()
