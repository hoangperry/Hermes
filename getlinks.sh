#!/bin/bash

export PYTHONPATH=$PWD
python3 getlinks.py --redis_host 172.18.0.4 --kafka_host 172.18.0.3
