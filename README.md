# DPS_Web_Crawler_Project

## Usage

docker: 

`docker-compose up`

non-docker 

`python3 prepare_for_running.py`

`python3 getlinks.py`

`python3 scraper.py`

noitice: scraper and getlinks can not run on one computer in the same time. 
Because getlinks will kill scraper's subprocess and vice versa.
