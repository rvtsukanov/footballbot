FROM python:3.8

WORKDIR /footballbot
COPY . /footballbot

ENV num_players=8
ENV PYTHONPATH /footballbot

RUN pip install -r requirements.txt

EXPOSE 5432

#CMD [ "python", "./server_v2.py" ]

