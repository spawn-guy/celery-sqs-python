# Celery Dockerized Testing Environment

This repository provides a Dockerized environment for testing Celery applications. It includes a Dockerfile, a docker-compose file, and a sample Celery application to demonstrate how to set up and run Celery workers and a Redis broker in a containerized environment.

## Prerequisites
- Docker
- Docker Compose
- Python 3.11
- Pipenv
- Redis (separate or uncomment in the included `docker-compose.yml`)

## Getting Started

1. Copy `.env.dist` to `.env` and adjust the environment variables as needed.
2. Copy `.env.docker.dist` to `.env.docker` and adjust the environment variables as needed (this is from inside docker env perspective).

## Running the Environment

2. Testing withOUT PyCURL
   1. delete/purge existing versions of docker container images
   2. ensure `pycurl=...` line is _disabled_ in `Pipfile`
   3. run `pipenv update --dev` to sync dependencies
   4. build and start Docker Compose environment
   5. run `app/stress_test.py` script from root folder


3. Testing WITH PyCURL
   1. delete/purge existing versions of docker container images
   2. ensure `pycurl=...` line is _enabled_ in `Pipfile`
   3. run `pipenv update --dev` to sync dependencies
   4. build and start Docker Compose environment
   5. run `app/stress_test.py` script from root folder

## AWS Elastic Beanstalk
it is possible to run this app as an AWS Elastic Beanstalk application.

1. deploy `Sample Application` `Python 3.11` as per AWS documentation. 
2. uncomment this line in `Pipfile` to install it correctly on `amazon linux 2023` environment: 
   ```
   pycurl = { version = "*", markers = "sys_platform != 'win32'", install_command = "pip install pycurl --global-option='--with-openssl' --compile" }
   ```
3. run `pipenv update -dev` to sync dependencies
4. deploy the application using `eb deploy` command.
5. update ENVIRONMENT variables in AWS Elastic Beanstalk console to match your `.env` file.
6. run `app/stress_test.py` script from root folder locally
