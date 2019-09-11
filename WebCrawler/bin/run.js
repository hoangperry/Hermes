const Template = require("./template")
const {domains} = require("../my_config")
const {repeat, name} = require("../my_config")

describe(name, function() {
    if(repeat > 0)
        for (let index = 0; index < repeat; index++) {
            Template(domains)
        }

    if(repeat === -1)
        while (true) {
            Template(domains)
        }
})
