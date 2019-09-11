#!/bin/bash

./ start_server_kafka.sh &&
sudo -S webdriver-manager update &&
webdriver-manager start
