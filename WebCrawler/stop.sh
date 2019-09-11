#!/bin/bash

sudo -S ./kafka/bin/kafka-server-stop.sh &&
sudo -S ./kafka/bin/zookeeper-server-stop.sh &&
sudo -S webdriver-manager shutdown
