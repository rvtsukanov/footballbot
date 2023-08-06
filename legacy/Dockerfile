FROM python:3.8
WORKDIR /footballbot
COPY .. /footballbot

RUN pip install -r requirements.txt

ENV num_players=8
ENV PYTHONPATH /footballbot

ENV FLASK_APP='routers.py'
ENV pg_db='test_data'

EXPOSE 5000

CMD ["python", "routers.py"]
#CMD [ "python", "./server_v2.py" ]

