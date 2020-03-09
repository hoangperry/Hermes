import requests
from application.crawler.configs import list_proxies


if __name__ == "__main__":
    print("HELLO")
    valid_proxies = list()
    for proxy in list_proxies:
        try:
            r = requests.get("https://www.newai.vn/app/demo/search.php", proxies=proxy)
            valid_proxies.append(proxy["http"])
        except Exception as ex:
            print(ex)
            print(proxy)

    wf = open("valid.txt", "w")
    valid_proxies = "\n".join(valid_proxies)
    wf.write(valid_proxies)