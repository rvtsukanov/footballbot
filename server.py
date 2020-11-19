from core import PollSession, Player, Message, Keyboard
import requests
import yaml
import json
from collections import deque
import pandas as pd
import time


TOKEN = yaml.safe_load(open('./config.yaml', 'r'))['token'][0]
API_PREFIX = 'https://api.telegram.org/bot{token}/{method_name}'


class Server:
    def __init__(self, update_rate, token, size_of_message_buffer=1000):
        self.update_rate = update_rate
        self.token = token

        self.message_buffer = deque(maxlen=size_of_message_buffer)
        self.size_of_message_buffer = size_of_message_buffer

        self.current_pollsession = {}


    def get_method_handle(self, method_name):
        return API_PREFIX.format(token=self.token, method_name=method_name)


    def get_request(self, method_name, params={}):
        return requests.get(url=self.get_method_handle(method_name=method_name),
                            params=params)


    def parse_player(self, json):
        return Player(**json)


    def parse_message(self, json):
        message_from = self.parse_player(json['from'])
        del json['from']
        return Message(**json, message_from=message_from)


    def parse_updates(self, response):
        response_json = response.json()['result']
        update_flag = False
        for update in response_json:
            message = update['message']
            msg = self.parse_message(message)
            if msg not in self.message_buffer:
                self.message_buffer.append(msg)
                update_flag = True

            if msg.text == 'sb':
                print(msg.message_from)
                self.send_message(chat_id=msg.message_from,
                                  text='Confirm', reply_markup=None)
                                  # reply_markup=Keyboard(inline=True, buttons=['Y', 'N']))

        return update_flag


    def update_messages(self):
        response = self.get_request('getUpdates')
        if response.ok:
            return self.parse_updates(response)


    def print_buffer(self):
        for msg in self.message_buffer:
            print(msg)


    def send_message(self, chat_id, text, reply_markup, params={}):
        params['chat_id'] = chat_id
        params['text'] = text
        params['reply_markup'] = reply_markup
        print(params)
        response = self.get_request(method_name='sendMessage', params=params)


    def run(self):
        while True:
            result = self.update_messages()

            if result:
                self.print_buffer()

            time.sleep(self.update_rate)






