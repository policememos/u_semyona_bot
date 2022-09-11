import json
import requests
from datetime import datetime
from settings import trello_api_key as api_key
from settings import my_token as my_token
from settings import id_board
from settings import todo_list_id
from settings import bot_key
import telebot


class TrelloConnector:
    headers = {
        "Accept": "application/json"
    }
    
    # def __init__(self ):
    #     ...


    def create_card(self, deliver_job):
        '''creates a new card'''
        url = "https://api.trello.com/1/cards"
        
        
        query = {
            'idList': todo_list_id,
            'key': api_key,
            'token': my_token,
            'name': deliver_job.address,
            'desc': deliver_job.description,
            'idLabels': deliver_job.type
        }
    
        response = requests.post(url,  headers=self.headers, params=query, timeout=1000)
        # oper_info = json.dumps(json.loads(response.text), sort_keys=True, indent=4, separators=(",", ": "))
        time = datetime.utcnow().strftime('%d.%m.%Y %H:%M')
        
        with open('log.txt', 'a', encoding='utf-8') as file:
            file.write((f'\n{time}\tStatus: {"Done" if response.status_code==200 else "Error"}\tAction: create card'))
            
            
        print(f'\nStatus: {"Done" if response.status_code==200 else "Error"}')


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
        
class DeliverJob:
    from_client_label = '6315d77a20bc67029658fd2f'
    to_client_label = '6315d77a20bc67029658fd38'
    
    def __init__(self, adress, type_, description):
        self.address = adress
        self.type_ = type_
        self.description = description
        
    @property
    def description(self):
        return self._description
    
    @description.setter
    def description(self, value):
        if isinstance(value, list):
            self._description = ' '.join(value)
        else:
            self._description = value.title()

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
    
    

# telegram bot

bot = telebot.TeleBot(bot_key, parse_mode='MarkdownV2')

@bot.message_handler(commands=['start', 'help', 'h'])
def send_welcome(message):
    last_chat_id = message.from_user.id
    bot.send_message(last_chat_id, '🤖')
    bot.send_message(last_chat_id, "Привет\! я могу добавить задание на доставку кроссовок\.\nНапиши про доставку в таком формате")
    bot.send_message(last_chat_id, '🏠 адрес: \<\?\>\n📌 что делаем: \<забрать/доставить\>\n✍🏼 описание: \<\?\>')
    bot.send_message(last_chat_id, '*Например:*\nвайнера 9\nзабрать\n88002000600, 18:00\-20:00 в пассаже ')
 
@bot.message_handler(func=lambda m: True)
def echo_all(message):
    last_chat_id = message.from_user.id
    adress, type_, *text = message.text.split('\n')
    trello = TrelloConnector()
    job = DeliverJob(adress, type_, text)
    trello.create_card(job)
    # bot.send_message(last_chat_id, '💡')
    bot.send_message(last_chat_id, '🏠⬅️👟' if job.type_ != '6315d77a20bc67029658fd38' else '👟➡️🙋🏽‍♂️')
    bot.send_message(last_chat_id, f'Карточка *{job.address}* добавлена\!')
 
if __name__ == '__main__':
    print('_____________________________________________________\n_______________ Bot status: Online __________________\n\n')
    bot.infinity_polling()
    print('\n\n_____________________________________________________\n_______________ Bot status: offline _________________')
    
    
