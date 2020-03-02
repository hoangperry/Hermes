FROM python:3.6

ENV CHROME_PACKAGE="google-chrome-stable_79.0.3945.88-1_amd64.deb"

ENV DISPLAY=:99
ENV DBUS_SESSION_BUS_ADDRESS=/dev/null

COPY . .
RUN apt-get update
RUN apt-get install -y xvfb wget dpkg libgconf-2-4
RUN wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
RUN apt -y install ./google-chrome-stable_current_amd64.deb
RUN apt-get install -f -y
RUN apt-get clean
RUN rm google-chrome-stable_current_amd64.deb
RUN pip install -r requirements.txt
RUN python3 prepare_for_running.py

RUN Xvfb :0 -ac -screen 0 1024x768x24 &

CMD python3 scraper.py
