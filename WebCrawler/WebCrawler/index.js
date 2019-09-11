const helper = require("./helper.js")        
const {topicOfKafka, log_link, kafkaOpts, redisOpts} = require("../my_config")
const redis = require('redis'),
        clientRedis = redis.createClient(redisOpts);
const kafka = require("kafka-node"),
    Producer = kafka.Producer,
    clientKafka = new kafka.KafkaClient(kafkaOpts),
    producer = new Producer(clientKafka);
const md5 = require("md5")
const sleep = require("sleep").sleep
const request = require("request")

class WebCrawler {

    /**
     * @param {String} url Link of domain
     */
    constructor(url){
        this.url = url
        if (typeof url !== "string")
            throw new Error("The URL must be string type!")
        if(!helper.isValidURL(url))
            throw new Error("The URL is unavailable!")
    }

    /**
     * open page function
     * @param {Function} callback Function will be execute after the browser open page
     */
    async openURL(callback){
        browser.get(this.url, 3000).then(() => {
            sleep(3)
            callback()
        })
    }

     /**
      * Caller recursive func
      * @param {Array<String} messages  list of message need store
      */
    storeData(messages){
        let index = 0
        this.writeData(messages, index)
    }

    /**
     * Store data in RedisDB and send to Kafka Server
     * @param {Array<String}messages 
     * @param {Number} index 
     */
    writeData(messages, index){
        if(index === messages.length){
            return
        }
        if(!helper.isValidURL(messages[index])){
            this.writeData(messages, index + 1)
            return
        }
        
        if(!helper.isSameDomain(this.url, messages[index])){
            this.writeData(messages, index + 1)
            return
        }

        const hash = md5(messages[index])
        clientRedis.exists(hash, async (err, reply) => {
            if(reply === 0){
                log_link ? console.log("ready: ", messages[index]) : null
                clientRedis.set(hash, "", () => {
                    producer.send([{topic: topicOfKafka, messages: messages[index]}], () => {
                        this.writeData(messages, index + 1)
                    })
                });
            }else {
                this.writeData(messages, index + 1)
            }
        })
    }

    /**
     *  Function get all href of <a> tags
     * @param {Function} callback Function will be execute after get href
     */
    async getAllHref(callback){
        if(!callback)
            return

        const elements = element.all(by.css("a[href]"))
        const hrefs = await  elements.map(async (item) => {
            // await browser.wait(protractor.ExpectedConditions.elementToBeClickable(item), 3000, 'Element taking too long to appear in the DOM')
            return  item.getAttribute("href")
        })
        callback(hrefs)
    }

    /**
     * Function 
     * @param {Number} id 
     * @param {*} value 
     * @param {Function} callback 
     */
    async chooseValueOfSelectorByID(id, value, callback){
        element(by.id(id)).all(by.tagName("option")).then( async items => {
            // await browser.wait(protractor.ExpectedConditions.elementToBeClickable(items[value]), 3000, 'Element taking too long to appear in the DOM')
            items[value].click().then(() =>{
                callback()
            })
        })
    }

    async elementClickByID(id, callback){
        const elt =  element(by.id(id))
        browser.wait(protractor.ExpectedConditions.presenceOf(elt), 10000, 'Element taking too long to appear in the DOM').then(async () =>{
            elt.click().then(callback)
        })
    }

    async elementClickByCSS(css, callback){
        const elt =  element(by.css(css))
        browser.wait(protractor.ExpectedConditions.presenceOf(elt), 10000, 'Element taking too long to appear in the DOM').then(async () =>{
            elt.click().then(callback)
        })
    }

    async elementClickByXpath(xpath, callback){
        const elt =  element(by.xpath(xpath))
        browser.wait(protractor.ExpectedConditions.presenceOf(elt), 10000, 'Element taking too long to appear in the DOM').then(async () =>{
            elt.click().then(callback)
        })
    }
}

module.exports = WebCrawler