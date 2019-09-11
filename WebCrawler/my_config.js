const CustomRegexForm = require("./custom_steps/CustomRegexForm")

module.exports = {
    default_regex: ".*\\d{6,}.*$",
    name: 'Web Crawler App',
    title:  'Get all link from {} page!',
    topicOfKafka: "bds",
    repeat: 1, //infinity loop: repeat = -1,
    log_link: true, //Log all link will be store,
    kafkaOpts: {
        kafkaHost: "localhost:9092"
    },
    redisOpts: {
        host: "localhost",
        port: 6379,
        db: 0
    },
    domains: [
        "https://alonhadat.com.vn",
        // "http://bannhasg.com",
        "https://dothi.net",
        "http://www.muabannhadat.vn",
        "https://muaban.net/mua-ban-nha-dat-cho-thue-toan-quoc-l0-c3",
        "https://www.nhadat.net/ban",
        "https://www.nhadat.net/cho-thue",
        "https://nhabansg.vn",
        "https://nha.chotot.com/toan-quoc/mua-ban-bat-dong-san",
        "https://nha.chotot.com/toan-quoc/thue-bat-dong-san",
        "https://mogi.vn/mua-nha-dat",
        "https://mogi.vn/thue-nha-dat",
        {
            url: "https://batdongsan.com.vn/nha-dat-cho-thue",
            steps: require("./custom_steps/batdongsan.com.vn").steps
        },
        {
            url: "https://batdongsan.com.vn/nha-dat-ban",
            steps: require("./custom_steps/batdongsan.com.vn").steps
        },
        {
            url: "http://diaoconline.vn",
            steps: CustomRegexForm(".*i\\d{6,}.*$")
        },
        {
            url: "https://nhadat24h.net",
            steps: CustomRegexForm(".*ID\\d{6,}.*$")
        }
    ]
}