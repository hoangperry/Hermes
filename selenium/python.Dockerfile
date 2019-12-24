FROM ubuntu:18.10

# set default environment

ENV DRIVER_PATH=/usr/bin/chromedriver

ENV KAFKA_HOSTS=127.0.0.1:9092 127.0.0.1:9093
ENV KAFKA_USER=None
ENV KAFKA_PASSWORD=None
ENV KAFKA_NUM_PARTITIONS=8
ENV KAFKA_LINK_TOPIC=None
ENV KAFKA_CONSUMER_GROUP=None

ENV REDIS_HOST=127.0.0.1
ENV REDIS_PORT=6379
ENV REDIS_DB=0
ENV REDIS_PASSWORD=None

ENV PG_HOST=127.0.0.1
ENV PG_PORT=5432
ENV PG_USER=postgres
ENV PG_PASSWORD=None
ENV PG_DB=data

ENV RESUME_STEP=100
ENV RESTART_SELENIUM_STEP=100

ENV USE_AWS=True
ENV CRAWL_TYPE=candidates
ENV DOWNLOAD_IMAGES=True

RUN apt-get update \
  && apt-get install -y python3-pip \
  && cd /usr/local/bin \
  && ln -s /usr/bin/python3 python \
  && pip3 install --upgrade pip \
  && apt-get install git -y

RUN wget -q -O - https://dl-ssl.google.com/linux/linux_signing_key.pub | apt-key add -
RUN sh -c 'echo "deb [arch=amd64] http://dl.google.com/linux/chrome/deb/ stable main" >> /etc/apt/sources.list.d/google-chrome.list'
RUN apt-get -y update
RUN apt-get install -y google-chrome-stable

# install chromedriver
RUN apt-get install -yqq unzip
RUN wget -O /tmp/chromedriver.zip http://chromedriver.storage.googleapis.com/`curl -sS chromedriver.storage.googleapis.com/LATEST_RELEASE`/chromedriver_linux64.zip
RUN unzip /tmp/chromedriver.zip chromedriver -d /usr/bin/

# https://github.com/TinDang97/DPS_Web_Crawler_Project.git
RUN git clone https://9d6a3cf8b4bbf744dcf4fd4ae8cf3f5d2dcdf077@github.com/TinDang97/DPS_Web_Crawler_Project.git

RUN pip3 install -r requirements.txt

WORKDIR /DPS_Web_Crawler_Project
#CMD ["python3"]
