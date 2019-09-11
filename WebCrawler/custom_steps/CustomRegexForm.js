const {filterLinkByReg} = require("../WebCrawler/helper")
const WebCrawler = require("../WebCrawler")


/**
 * @param {String} custom_regex
 */
module.exports = CustomRegexForm  = (custom_regex) => (webCrawler) => {
    webCrawler.getAllHref((hrefs) => {
        filterLinkByReg(hrefs, custom_regex, (hrefFiltered) => {
            webCrawler.storeData(hrefFiltered)
        })
    })
}