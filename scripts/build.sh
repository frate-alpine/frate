#!/bin/bash

source virtualenvwrapper.sh

cd /var/www/frate

git pull origin master

workon frate

pip install -r freeze.txt
bower install
python manage.py migrate
python manage.py collectstatic
fab uwsgi

deactivate
