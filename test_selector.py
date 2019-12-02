from crawler.application.common.crawler.scrapping import WebDriverWrapper


if __name__ == "__main__":

    webdriver = WebDriverWrapper(executable_path=None)

    webdriver.get("https://dinhgianhadat.vn/tin-mat-duong-261-dong-khe-395trm2-4431783")

    while True:
        try:
            query = input("Query: ")
            dt = webdriver.test_select(query)
            print(dt)

            if dt is not None:
                print("-----------------------------")
                print("-----------------------------")
                print("-----------------------------")
                for d in dt:
                    print(d.text)
        except:
            pass