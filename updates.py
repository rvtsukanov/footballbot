import requests
import yaml
from core import Player
import json

TOKEN = yaml.safe_load(open('./config.yaml', 'r'))['token'][0]
# API_PREFIX = 'https://api.telegram.org/bot{token}/{method_name}'
#
#
# def get_method_handle(method_name, token=TOKEN):
#     return API_PREFIX.format(token=token, method_name=method_name)
#
#
# def getUpdates():
#     return requests.get(get_method_handle(method_name='getUpdates'))
#
# def Update():
#     return requests.get(get_method_handle(method_name='Update'))
#
#
# response = getUpdates().json()
# # print(response)
#
# def parse_updates_for_creating_player(updates, no):
#     return (
#         updates['result'][no]['message']['from']['id'],
#         updates['result'][no]['message']['from']['username'],
#         updates['result'][no]['message']['from']['first_name'],
#         updates['result'][no]['message']['from']['last_name'],
#         updates['result'][no]['message']['message_id'],
#         updates['result'][no]['message']['text']
#     )
#
# for no in range(1):
#     print(parse_updates_for_creating_player(response, no=no))
#
#



#
#
# def sendMessage(chat_id, text, keyboard=None, **kwargs):
#     return requests.get(get_method_handle(method_name='sendMessage'),
#                         params={'chat_id': chat_id,
#                                 'text': text,
#                                 'reply_markup': keyboard
#                                 })
#
# def sendLocation(chat_id):
#     return requests.get(get_method_handle(method_name='sendLocation'),
#                         params={'chat_id': chat_id,
#                                 'latitude': 55.718779,
#                                 'longitude': 37.551103}
#                                )
#

# json.dumps(kb_markup)
# print(kb_markup)
# print(json.dumps(kb_markup))

# reply = sendMessage(chat_id="188727612", text='hi maboi', keyboard=json.dumps(kb_markup))
# reply = sendMessage(chat_id="188727612", text='1', keyboard=json.dumps(kb_markup_remove))
# reply = sendLocation(chat_id="188727612")
# print(reply.text)

# 188727612

# idx, username, name, surname, mid, text =
# print(idx, username, name, surname, mid, text)

# test_player = Player(id=idx, username=username, name=name, surname=surname, agreed=True, is_admin=False)

# print(test_player.id)


from server import Server

server = Server(update_rate=1, token=TOKEN)

server.run()