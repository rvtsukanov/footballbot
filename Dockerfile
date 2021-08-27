FROM python:3.8

COPY . .

ENV num_players=8

RUN pip install -r requirements.txt

#EXPOSE 5000

CMD [ "python", "./server_v2.py" ]

