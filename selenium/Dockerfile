FROM ubuntu:18.10


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
