FROM python:3.6

ENV PYTHONUNBUFFERED 1

RUN mkdir -p /opt/app

WORKDIR /opt/app

RUN pip install gunicorn

ADD requirements.txt /opt/app/
RUN pip install -r requirements.txt
ADD . /opt/app/
ENV DJANGO_SETTINGS_MODULE isucon.portal.docker_settings

RUN python manage.py collectstatic --noinput

CMD ["gunicorn", "isucon.portal.wsgi:application", "-b", "0.0.0.0:5000"]

EXPOSE 5000
