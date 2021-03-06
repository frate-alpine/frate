FROM ubuntu:16.04

RUN apt-get update
RUN apt-get install -y \
  python python-dev python-pip \
  nginx \
  curl git \
  zlib1g libjpeg8 libjpeg8-dev libfreetype6 libfreetype6-dev \
  supervisor

RUN curl -kL git.io/nodebrew | perl - setup
ENV PATH /root/.nodebrew/current/bin:$PATH
RUN nodebrew install-binary v4.4.3
RUN nodebrew use v4.4.3


RUN \
  chown -R www-data:www-data /var/lib/nginx && \
  echo "\ndaemon off;" >> /etc/nginx/nginx.conf && \
  rm /etc/nginx/sites-enabled/default

RUN npm i -g bower

ADD nginx/frate.conf /etc/nginx/sites-enabled
ADD supervisor.conf /etc/supervisor/conf.d/

RUN mkdir -p /var/www/frate
WORKDIR /var/www/frate

ADD requirements.txt ./requirements.txt
RUN pip install -r requirements.txt
ADD .bowerrc ./.bowerrc
ADD bower.json ./bower.json
RUN bower install --allow-root

ADD . /var/www/frate

ENV DJANGO_SETTINGS_MODULE core.settings.prod

RUN python manage.py collectstatic --noinput

CMD \
  python manage.py migrate && \
  /usr/bin/supervisord

EXPOSE 80
