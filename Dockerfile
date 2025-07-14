# pull official base image
#FROM python:3.11-slim
FROM python:3.11

# set work directory
WORKDIR /usr/src

RUN mkdir /data && chmod 666 /data

# set environment variables
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

# install dependencies
# celery/kombu limitation
RUN pip install --upgrade setuptools==59.6.0

RUN pip install pipenv
COPY ./Pipfile .
COPY ./Pipfile.lock .
RUN pipenv install --system --deploy --ignore-pipfile

# copy .env
COPY ./.env.docker ./.env

# copy project
COPY app ./app
