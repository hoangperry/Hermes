const WebCrawler = require("../WebCrawler")
const helper = require("../WebCrawler/helper.js")
const format = require('string-format')
const {default_regex, title, name } = require("../my_config")

/**
 * @param {Array} domains The domain list
 * @param {Function} nextSteps The string
 */
const Layout = (domains, nextSteps) => {
    domains.forEach(domain => {
        browser.waitForAngularEnabled(domain.isAgular ? domain.isAgular : false);
        const url = domain.url ? domain.url : domain
        it(format(title,  url),  async function() {
            const webCrawler = new WebCrawler(url)
            //navigate to page
            webCrawler.openURL(() => {
                nextSteps(webCrawler, domain.steps ? domain.steps : null)
            })
        })
    })
}

/**
 * @param {Array<String>} domains The domain list
 */
module.exports = Template = (domains) => (
    Layout(domains, (webCrawler, steps) => {
        if(steps){
            steps(webCrawler)
            return
        }

        webCrawler.getAllHref((hrefs) => {
            helper.filterLinkByReg(hrefs, default_regex, (hrefFiltered) => {
                webCrawler.storeData(hrefFiltered)
            })
        })
    })
)