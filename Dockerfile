FROM python:3.11

# Copying all stuff inside the WORKDIR
WORKDIR /usr/src/footballbot
COPY . .

# Installing dependencies
RUN pip install -r requierments.txt
RUN apt-get update && apt-get -y install vim

#ENV DATABASE_URI=sqlite:////var/lib/database2/database.db
ENV FLASK_DEBUG=False
ENV FLASK_PRODUCTION_SERVER=True
VOLUME /var/lib/database2/:/var/lib/database2

EXPOSE 443

WORKDIR /usr/src/footballbot/footballbot

RUN ["chmod", "+x", "../yc/run_flask.sh"]
#RUN ["sudo", "mkdir", "/var/lib/database2"]
CMD ["../yc/run_flask.sh"]

