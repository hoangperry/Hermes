#!/bin/bash

export DRIVER_PATH=/usr/bin/chromedriver

export KAFKA_HOSTS=192.168.2.123:9092
export KAFKA_USER=admin
export KAFKA_PASSWORD=Dps@123234#
export KAFKA_NUM_PARTITIONS=8
export KAFKA_LINK_TOPIC=default
export KAFKA_CONSUMER_GROUP=default

export REDIS_HOST=192.168.2.123
export REDIS_PORT=6379
export REDIS_DB=0
export REDIS_PASSWORD=Dps@123234#

export PG_HOST=192.168.2.184
export PG_PORT=5432
export PG_USER=dps_admin
export PG_PASSWORD=Dps@123234#
export PG_DB=data

export RESUME_STEP=100
export RESTART_SELENIUM_STEP=100

export USE_AWS=True
export CRAWL_TYPE=candidates
export DOWNLOAD_IMAGES=True
