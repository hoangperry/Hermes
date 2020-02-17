list_proxies = list()

lines = open("proxies.txt").readlines()

for line in lines:
    url = line.strip()
    proxy = {
        "http": "http://kimnt93:989776@" + url,
        "https": "http://kimnt93:989776@" + url
    }
    list_proxies.append(proxy)
