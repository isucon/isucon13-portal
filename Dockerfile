FROM python:3.11 AS app

RUN pip install --upgrade pip && pip install pipenv
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    ca-certificates nginx locales locales-all \
    && apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN locale-gen ja_JP.UTF-8


RUN mkdir /opt/app
WORKDIR /opt/app

RUN pip install mysqlclient psycopg2-binary gunicorn

ENV PYTHONPATH=/opt/app/
ENV DJANGO_SETTINGS_MODULE=isucon.portal.docker_settings
ADD Pipfile /opt/app/
ADD Pipfile.lock /opt/app/
RUN pipenv install --system

ADD manage.py /opt/app/
ADD isucon/ /opt/app/isucon/

# NGINX
RUN python manage.py collectstatic --noinput
RUN rm -v /var/www/html/*
ADD htdocs/ /var/www/html/
RUN ln -s /opt/app/static /var/www/html/static
ADD files/nginx.conf /etc/nginx/nginx.conf
ADD files/default.conf /etc/nginx/sites-enabled/default

EXPOSE 80

ADD files/entrypoint.sh /opt/app/
ENTRYPOINT [ "/opt/app/entrypoint.sh" ]
