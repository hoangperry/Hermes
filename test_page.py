from application.service.realestate import RealEstateExtractService

if __name__=="__main__":
    real_estate_scraper = RealEstateExtractService(
        selenium_driver=None,
        rule_dir="rules/realestate/",
        kafka_consumer_bsd_link="links",
        kafka_object_producer="links",
        object_topic="links"
    )
    url = "https://batdongsan.com.vn/cho-thue-can-ho-chung-cu-duong-quoc-lo-13-xa-hung-dinh-prj-first-home-premium-binh-duong/nha-nguyen-tang-cao-view-dep-city-tower-va-citadines-luxury-residence-gan-aeon-pr21856496"

    real_estate_scraper.set_page(url)
    dbfield = real_estate_scraper.get_data_field()
    result = real_estate_scraper.normalize_data(dbfield)

    print(result)
