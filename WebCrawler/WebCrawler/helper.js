const URL = require('url').parse;

/**
 *  Check is valid URL
 * @param {String} str 
 */
const isValidURL = (str) => {
    var res = str.match(/(http(s)?:\/\/.)?(www\.)?[-a-zA-Z0-9@:%._\+~#=]{2,256}\.[a-z]{2,6}\b([-a-zA-Z0-9@:%_\+.~#?&//=]*)/g);
    return (res !== null)
};

/**
 * this func help filter link match with your regex
 * @param {Array<String>} lstUrl 
 * @param {String} regex 
 * @param {Function} callback 
 */
const filterLinkByReg = async (lstUrl, regex, callback) => {
    const reg = new RegExp(regex)
    callback( await lstUrl.filter(url => {
        if(reg.test(url))
            return url
    }))
}

/**
 * Check url and domain are as same as host 
 * @param {String} domain 
 * @param {String} url 
 */
const isSameDomain = (domain, url) =>{
   return URL(domain).host === URL(url).host
}

module.exports = {
    isValidURL,
    filterLinkByReg,
    isSameDomain
}