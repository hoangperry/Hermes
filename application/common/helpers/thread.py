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
        # sleep 1 minutes
        time.sleep(60 * 1)
    elif 11 < hour <= 14:
        # take a snap
        # sleep 25 minutes
        time.sleep(60 * 3)
    elif 14 < hour <= 21:
        # sleep 10 minutes
        time.sleep(60 * 1)
    elif 21 < hour <= 24:
        # sleep 2 hours
        time.sleep(60 * 60 * 2)
    elif 0 <= hour <= 5:
        # sleep 4 hours
        time.sleep(60 * 60 * 3)
    else:
        # sleep 2 hours
        time.sleep(60 * 60 * 1)
