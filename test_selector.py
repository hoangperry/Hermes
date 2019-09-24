from application.common.crawler.scrapping import WebDriverWrapper


if __name__ == "__main__":

    webdriver = WebDriverWrapper(executable_path=None)

    webdriver.get("https://batdongsan.com.vn/cho-thue-can-ho-chung-cu-duong-quoc-lo-13-xa-hung-dinh-prj-first-home-premium-binh-duong/nha-nguyen-tang-cao-view-dep-city-tower-va-citadines-luxury-residence-gan-aeon-pr21856496")

    while True:
        try:
            query = input("Query: ")
            dt = webdriver.test_select(query)
            print(dt)
        except:
            pass