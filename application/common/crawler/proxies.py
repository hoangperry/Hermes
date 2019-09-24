
list_proxies = list()

with open("proxies.txt") as line:
    url = line.read().strip()
    proxy = {
        "http": "http://kimnt93:989776@" + url,
        "https": "http://kimnt93:989776@" + url
    }
    list_proxies.append(proxy)
