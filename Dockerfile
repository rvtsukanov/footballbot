FROM python:3.11

# Copying all stuff inside the WORKDIR
WORKDIR /usr/src/footballbot
COPY . .

# Installing dependencies
RUN pip install -r requierments.txt
RUN apt-get update && apt-get -y install vim

# Init db?
# RUN flask init db

EXPOSE 8443:5003

WORKDIR /usr/src/footballbot/footballbot

RUN ["chmod", "+x", "../yc/run_flask.sh"]
CMD ["../yc/run_flask.sh"]

