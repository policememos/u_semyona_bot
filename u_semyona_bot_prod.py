import json
import requests
from datetime import datetime
from settings import trello_api_key as api_key
from settings import my_token as my_token
from settings import id_board
from settings import todo_list_id
from settings import bot_key
from settings import areas_id
from settings import custom_field_id
from streets_list import streets_map
import logging
from aiogram import Bot, Dispatcher, executor, types


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

logging.basicConfig(level=logging.INFO)

bot = Bot(token=bot_key, parse_mode='HTML')
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
 
if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)

    
    
