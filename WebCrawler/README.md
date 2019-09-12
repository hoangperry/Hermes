# DPS Web Crawler

The agent help to get all link from domains.

## Installation

Use the package manager [NPM](https://pip.pypa.io/en/stable/) to install DPS Web Crawler.

```bash
npm install protractor kafka-node md5 redis sleep string-format --save
```

Use the [WebDriverManager](https://www.npmjs.com/package/webdriver-manager) to automate the management of the binary drivers.

```bash
npm install -g webdriver-manager
```

## Pre-process
Clone this project:

```git
git clone https://github.com/TinDang97/DPS_Web_Crawler_Project
```
Start require server:

```bash
bash ./start_server.sh
```
Start [Protractor](https://www.protractortest.org) server:

```bash
protractor protractor_conf.js
```

## Usage

You can change [my_config.js]() adapt with your requirement.
Example:
```node
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
        {
            url: "https://nhadat24h.net",
            steps: CustomRegexForm(".*ID\\d{6,}.*$")
        }
    ]
}

```

Define [KafkaCosumer](https://www.npmjs.com/package/kafka-node#consumer) to listening with nodejs. Example:
```node
const kafka = require("kafka-node"),
Consumer = kafka.Consumer,
    clientKafka = new kafka.KafkaClient(kafkaOpts),
    consumer = new Consumer(clientKafka, 
        [
            { topic: 't', partition: 0 }, { topic: 't1', partition: 1 }
        ],
        {
            autoCommit: false
        });

consumer.on('message', function (message) {
    console.log(message);
});
```
## Contributing
Pull requests are welcome. For major changes, please open an issue first to discuss what you would like to change.

Please make sure to update tests as appropriate.

## License
[DPS](https://www.dps.com.vn/)
