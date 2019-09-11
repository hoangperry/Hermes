exports.config = {
    seleniumAddress: 'http://localhost:4444/wd/hub',
    specs: ["./bin/run.js"],
    capabilities:{
        'directConnect': true,
        'browserName': 'chrome',
        chromeOptions: {
            args: [
                // "--headless", 
                // "--disable-gpu", 
                "--window-size=800,600",
                "--remote-debugging-port=9969",
                "--ignore-certificate-errors",
                "--ignore-urlfetcher-cert-requests",
                "--allow-running-insecure-content",
                "--no-sandbox'"
            ]
        }
    }
}