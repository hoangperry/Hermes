from datetime import datetime
import time


def sleep_by_hour():
    hour = datetime.now().hour

    if 7 <= hour <= 11:
        # sleep 5 minutes
        time.sleep(60 * 5)
    elif 11 < hour <= 14:
        # take a snap
        # sleep 25 minutes
        time.sleep(60 * 25)
    elif 14 < hour <= 21:
        # sleep 10 minutes
        time.sleep(60 * 10)
    elif 21 < hour <= 24:
        # sleep 2 hours
        time.sleep(60 * 60 * 2)
    elif 0 <= hour <= 5:
        # sleep 4 hours
        time.sleep(60 * 60 * 4)
    else:
        # sleep 2 hours
        time.sleep(60 * 60 * 2)


def real_estate_sleep():
    hour = datetime.now().hour

    if 7 <= hour <= 11:
        time.sleep(30)
    elif 11 < hour <= 14:
        time.sleep(120)
    elif 14 < hour <= 21:
        time.sleep(30)
    elif 21 < hour <= 24:
        # sleep 2 hours
        time.sleep(3600)
    elif 0 <= hour <= 5:
        # sleep 4 hours
        time.sleep(3600)
    else:
        # sleep 2 hours
        time.sleep(600)
