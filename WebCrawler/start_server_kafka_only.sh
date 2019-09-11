#!/bin/bash

sudo -S bash ./kafka/bin/zookeeper-server-start.sh -daemon ./kafka/config/zookeeper.properties &&
sleep 1 &&
sudo -S bash ./kafka/bin/kafka-server-start.sh -daemon ./kafka/config/server.properties
