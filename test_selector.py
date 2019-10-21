from application.common.crawler.scrapping import WebDriverWrapper


if __name__ == "__main__":

    webdriver = WebDriverWrapper(executable_path=None)

    webdriver.get("https://itviec.com/it-jobs/django-python-developers-snap-shop-0056")

    while True:
        try:
            query = input("Query: ")
            dt = webdriver.test_select(query)
            print(dt)

            if dt is not None:
                print("-----------------------------")
                print("-----------------------------")
                print("-----------------------------")
                print(dt[0].text)
        except:
            pass