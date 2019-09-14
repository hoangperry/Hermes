from runable import realestate
import argparse

# Instantiate the parser
parser = argparse.ArgumentParser()

parser.add_argument("--rule_dir", required=True, help="Rules directory")
parser.add_argument("--log_dir", required=False, help="Logs directory")
parser.add_argument("--selenium_driver", required=False, help="Selenium driver directory")

# web crawler params
parser.add_argument("--proxy_file", required=False, help="Proxy file, each line contains http/https proxy", type=str)
parser.add_argument("--domain_file", required=False, type=str, help="Domain files")

args = parser.parse_args()

if args.log_dir is None:
    args.log_dir = 'logs/'

if args.proxy_file is None:
    args.proxy_file = ''

if args.selenium_driver is None:
    args.selenium_driver = None

if args.domain_file is None:
    args.domain_file = None

if __name__ == "__main__":
    realestate.run(args.proxy_file, args.rule_dir, args.selenium_driver)
