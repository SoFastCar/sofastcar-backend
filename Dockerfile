FROM        python:3.7-slim

RUN         apt-get -y -qq update && \
            apt-get -y -qq dist-upgrade && \
            apt-get -y -qq autoremove

RUN         apt -y install nginx

COPY        ./requirements.txt /tmp/
RUN         pip install -r /tmp/requirements.txt

COPY        . /srv/sofastcar
WORKDIR     /srv/sofastcar/app

RUN         rm /etc/nginx/sites-enabled/default
RUN         cp /srv/sofastcar/.config/sofastcar.nginx /etc/nginx/sites-enabled/
RUN         mkdir /var/log/gunicorn
RUN         mkdir /srv/sofastcar/app/static

CMD         /bin/bash