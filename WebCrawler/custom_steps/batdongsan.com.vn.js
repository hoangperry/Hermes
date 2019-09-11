const {filterLinkByReg} = require("../WebCrawler/helper")
const WebCrawler = require("../WebCrawler")

/**
 * @param {WebCrawler} webCrawler
 */
module.exports.steps = (webCrawler) => {
    const custom_regex = ".*pr\\d{6,}.*$"
    webCrawler.chooseValueOfSelectorByID("ddlSortReult", 1, () => {
        webCrawler.getAllHref((hrefs) => {
            filterLinkByReg(hrefs, custom_regex, (hrefFiltered) => {
                webCrawler.storeData(hrefFiltered)
            })
        })
    })
}