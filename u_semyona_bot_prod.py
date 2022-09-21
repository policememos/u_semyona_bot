import json
import requests
import os

from datetime import datetime
from streets_list import streets_map

# from aiogram import Bot, Dispatcher, executor, types


import asyncio
import logging

from aiogram import Bot, types
from aiogram.dispatcher import Dispatcher
from aiogram.utils.executor import start_webhook

api_key = os.getenv('api_key')
my_token = os.getenv('my_token')
id_board = os.getenv('id_board')
todo_list_id = os.getenv('todo_list_id')
bot_key = os.getenv('bot_key')
custom_field_id = os.getenv('custom_field_id')

areas_id ={
'631d9c91b9b1b40281c2b09e': 'Академический',
'631d9c9d62eac501a94a5e77': 'Широкая Речка',
'631d9ca05edcb904e747ecd6': 'Заречный',
'631d9ca5502dff0295ff2080': 'Визовский',
'631d9caaa22b8101e44cb459': 'Лиственный',
'631d9caefa21c900cba3f3bd': 'Вокзальный',
'631d9cb645a10001859fb7c2': 'Новая Сортировка',
'631d9cb93a98690217fea434': 'Семь Ключей',
'631d9cbc6da1910205b8e63c': 'Старая Сортировка',
'631d9cc0b2d0ed014fdf7105': 'поселок Палкино',
'631d9cc299e7790036a4ceb4': 'Калиновский',
'631d9cc512be9902ca6e4071': 'Комсомольский',
'631d9cc7072464027c968f42': 'Втузгородок',
'631d9ccaf0446400d28ae4cc': 'ЖБИ',
'631d9ccd284f9a03548ee968': 'Изоплит',
'631d9ccf95723701ea140093': 'Пионерский',
'631d9cd26a70e100688e8fd8': 'Шарташский',
'631d9cd6dff9d20101be96fe': 'Краснолесье',
'631d9cda5650fe03698fcc6a': 'поселок Совхозный',
'631d9cdd437099015da0746a': 'Центр',
'631d9ce1d8a2d401048ad67e': 'Юго-Западный',
'631d9ce4d673d70196ae3e6d': 'Компрессорный',
'631d9ce62615d80261b88570': 'Лечебный',
'631d9ce8e2f7ed0188b51dee': 'Кольцово',
'631d9ceb39340e0036c629e2': 'Птицефабрика',
'631d9ced53128100a168cbc5': 'Синие Камни',
'631d9cf11d1448011fe8bd94': 'Парковый',
'631d9cf4361ad30091d7ba24': 'Малый Исток',
'631d9cf724d53d0024e0a0dc': 'Уралмаш',
'631d9cfa8b92db033aefc80e': 'Эльмаш',
'631d9cfcb7f585013491db3e': 'Ботанический',
'631d9cfe55ad830116482551': 'Вторчермет',
'631d9d03b5720f007e13fb83': 'Елизавет',
'631d9d051cec840174440181': 'Химмаш',
'631d9d07a0c2240296b69a3e': 'Нижнеисетский',
'631d9d0ae2be8b01fe69c408': 'Рудный',
'631d9d0c29b1fb007736235a': 'Уктусский',
'631d9d0f277d7a016cd4eb13': 'Южный'
}


class DeliverJob:
    from_client_label = '6315d77a20bc67029658fd2f'
    to_client_label = '6315d77a20bc67029658fd38'
    
    def __init__(self, address, type_, description, user_name):
        self.address = address
        self.user_name = user_name
        self.type_ = type_
        self.area = address
        self.description = description
        self.custom_field_id = self.get_custom_field_id(self._area)
        
    def get_custom_field_id(self, area):
        if area != 'Не определено':
            _id = [k for k, v in areas_id.items() if area == v][0]
            return _id
        return ''
        
        
    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        if isinstance(value, list):
            self._description = f'`Район: {self._area}`\n'+' '.join(value)
        else:
            self._description = f'`Район: {self._area}`\n'+value.title()

    @property
    def type_(self):
        return self._type
    
    @type_.setter
    def type_(self, value):
        pattern = ['доставка', 'доставить', 'клиенту', 'к', 'до']
        self._type = self.to_client_label if value.lower() in pattern else self.from_client_label
    
    @property
    def address(self):
        return self._address
    
    @address.setter
    def address(self, value):
        self._address = value.title()
        
    @property
    def area(self):
        return self._area
    
    @area.setter
    def area(self, value):
        def is_it_num(s):
            for i in s:
                try:
                    int(i)
                    return False
                except ValueError:
                    return True
                
        t =value.split(',')[0].split()
        temp = [x for x in t if  all(map(is_it_num, x)) ]
        street = ' '.join(temp).lower()
        
        for k, v in streets_map.items():
            if street in v:
                self._area = k
                break
        else:
            self._area = 'Не определено'


class TrelloConnector:
    headers = {
        "Accept": "application/json"
    }
    
    # def __init__(self ):
    #     ...


    def create_card(self, job: DeliverJob):
        '''creates a new card'''
        url = "https://api.trello.com/1/cards"
        
        
        query = {
            'idList': todo_list_id,
            'key': api_key,
            'token': my_token,
            'name': job.address,
            'desc': job.description,
            'idLabels': job.type_
        }
    
        response = requests.post(url,  headers=self.headers, params=query, timeout=1000)
        # oper_info = json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
        time = datetime.utcnow().strftime('%d.%m.%Y %H:%M')
        card_id = response.text[7:31]
        self.custom_field_area(card_id, value=job.custom_field_id, user_name=job.user_name)
        
        with open('log.txt', 'a', encoding='utf-8') as file:
            file.write((f'\n{time}\tStatus: {"Done" if response.status_code==200 else "Error"}\tAction: create card\tUser: {job.user_name}'))      
            
        print(f'\n Status: {"Done" if response.status_code==200 else "Error"}\tAction: create card\tUser: {job.user_name}')

    def custom_field_area(self, card_id, user_name, value=None):
        url = f"https://api.trello.com/1/cards/{card_id}/customField/{custom_field_id}/item"

        headers = {
        "Content-Type": "application/json"
        }

        query = {
        'key': api_key,
        'token': my_token
        }

        payload = json.dumps( {
             "idValue": value, #id of area from map
        } )

        response = requests.request("PUT", url, data=payload, headers=headers, params=query, timeout=1000)

        print(f'\n Status: {"Done" if response.status_code==200 else {response.status_code}}\tAction: custom_field to card\tUser: {user_name}, text:{response.text}')
          

    def get_label_info(self):
        '''gets labels from board'''
        
        url = f"https://api.trello.com/1/boards/{id_board}/labels"
        query = {
            'key': api_key,
            'token': my_token
        }

        response = requests.get(url,  headers=self.headers, params=query, timeout=1000)
        data = response.json()
        print('id of label\t\t  label name')
        print('-'*36)
        if len(data) > 1:
            for i in data:
                a = (i.get('id'), i.get('name'))
                print(*a, sep ='  ' )
        
        else:
            print((i.get('id'), i.get('name')))
            
        time = datetime.utcnow().strftime('%d.%m.%Y %H:%M')
        
        print(f'\n{time}\tStatus: {"Done" if response.status_code==200 else "Error"}')
        
        with open('log.txt', 'a', encoding='utf-8') as f:
            f.write(f'\n{time}\tStatus: {"Done" if response.status_code==200 else "Error"}\tAction: get label info')
            
    def get_custom_fields(self):
        url = f"https://api.trello.com/1/boards/{id_board}/customFields"

        headers = {
        "Accept": "application/json"
        }

        query = {
        'key': api_key,
        'token': my_token
        }

        response = requests.request("GET", url, headers=headers, params=query)
        
        with open('outputfile.json', 'wb') as f:
            f.write(response.content)
        print(response.status_code)

    def get_board_info(self):
        url = f"https://api.trello.com/1/boards/{id_board}"

        headers = {
        "Accept": "application/json"
        }

        query = {
        'key': api_key,
        'token': my_token
        }

        response = requests.request("GET", url, headers=headers, params=query )
        with open('outputfile.json', 'wb') as f:
            f.write(response.content)
        print(response.status_code)
        


                

# telegram bot
API_TOKEN = bot_key

WEBHOOK_HOST = 'https://your.domain'  # Domain name or IP addres which your bot is located.
WEBHOOK_PATH = '/path/to/api'
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

# webserver settings
WEBAPP_HOST = 'localhost'  # or ip
WEBAPP_PORT = 3001

logging.basicConfig(level=logging.INFO)

loop = asyncio.get_event_loop()
bot = Bot(token=API_TOKEN, loop=loop, parse_mode='HTML')
dp = Dispatcher(bot)


@dp.message_handler(commands=['start', 'help', 'h'])
async def send_welcome_(message):
    last_chat_id = message.from_user.id
    await bot.send_message(last_chat_id, '🤖')
    await bot.send_message(last_chat_id, "Привет! я могу добавить задание на доставку кроссовок.\nНапиши про доставку в таком формате")
    await bot.send_message(last_chat_id, '🏠 адрес: ???\n📌 что делаем: забрать/доставить\n✍🏼 описание: ???')
    await bot.send_message(last_chat_id, '<b>Например:</b>\nвайнера 9\nзабрать\n2 этаж, кв43, 88002000600, 18:00-20:00 в пассаже ')
 
@dp.message_handler()
async def echo_all_(message):
    last_chat_id = message.from_user.id
    user_name = message.from_user.first_name + ' ' + message.from_user.last_name
    print(user_name)
    adress, type_, *text = message.text.split('\n')
    trello = TrelloConnector()
    job = DeliverJob(adress, type_, text, user_name)
    trello.create_card(job)
    # bot.send_message(last_chat_id, '💡')
    await bot.send_message(last_chat_id, '🏠⬅️👟' if job.type_ != '6315d77a20bc67029658fd38' else '👟➡️🙋🏽‍♂️')
    await bot.send_message(last_chat_id, f'Карточка <b>{job.address}</b> добавлена!')
 

    
    
