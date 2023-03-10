
import requests
from pprint import pprint
import os
import yadisk
from datetime import datetime
import json
import urllib.request
from alive_progress import alive_bar
import time
import shutil


with open(r'API vk\token.txt', 'r') as file_object:
    token = file_object.read().strip()
# with open(r'API vk\token_ya.txt', 'r') as file_object:
#     TOKEN = file_object.read().strip()


URL = 'https://cloud-api.yandex.net/v1/disk/resources'
headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {TOKEN}'}


def create_folder(path):
    """Создание папки. \n path: Путь к создаваемой папке."""
    requests.put(f'{URL}?path={path}',headers = headers)
    print('Создали папку "Import Photo From VK" на вашем яндекс диске')

create_folder('Import Photo From VK')

    




class VkUser:
    url = 'https://api.vk.com/method/'
    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }
    
    def upload_photo(self,path,counter = 5):
        uploader = yadisk.YaDisk(token = Yaid)
        count = 0
        with alive_bar(counter) as bar:      
            for address,dirs, files in os.walk(path):
                for file in files:  
                    if count < counter:                    
                        if uploader.is_file(f'/Import Photo From VK/{file}'):
                            uploader.remove(f'/Import Photo From VK/{file}',permanently = True)
                            print(f"Предыдущий файл с названием {file} был удалён.")
                            print('---------------')
                            uploader.upload(f'{address}/{file}', f'/Import Photo From VK/{file}')
                            print(f'Файл {file} загружен')
                            print('---------------')
                            count += 1
                            bar()
                            time.sleep(0.5) #16659465 
                                
                                
                        else:
                            uploader.upload(f'{address}/{file}', f'/Import Photo From VK/{file}')
                            print(f'Файл {file} загружен')
                            print('---------------')
                            count += 1
                            bar()
                            time.sleep(0.5) #16659465 
        path = os.path.join(os.path.abspath(os.path.dirname(__file__)), 'VK_photo')
        shutil.rmtree(path)

        if count < counter:
            print(f'Всего в папке было файлов : {count}, поэтому записали файлов: {count} , а не {counter}')
        print('Удалили временную папку VK_photo c компьютера ')
        print() 

        print(f'Ссылка на обновленный Яндекс диск : {r"https://disk.yandex.ru/client/disk/Import%20Photo%20From%20VK"}')
                    


    def search_photos(self,owner_id):
        search_photos_url=self.url+'photos.get'
        search_photos_params ={
            'owner_id': owner_id,
            'album_id':'profile',
            'extended' : '1',
            'count':100
            }
 
        res = requests.get(search_photos_url,params={**self.params, **search_photos_params}).json()
        data = res['response']['items']
        
        
        d = {}
        
        for i in data:
            key = f"{i['likes']['count']}.jpg"
            key1 = f"{i['likes']['count']}_date_{(datetime.utcfromtimestamp(i['date']).strftime('%d-%m-%Y_%H-%M-%S'))}.jpg"
            if key not in d.keys():
                file_name = key
            else:
                file_name = key1
            max_size = 0
            

            for size in i['sizes']:
                if size['height'] > 0:
                    if size['height'] > max_size:
                        d[file_name] = {'url':size['url'],'type':size['type']}
                        max_size = size['height']
                else:
                    d[file_name] = {'url':i['sizes'][-1]['url'],'type':i['sizes'][-1]['type']}
            
        
        json_dict = [{"file_name":i, "type":d[i]["type"] } for i in d ]
        with open("data_photo.json", "w") as file:
            json.dump(json_dict, file)
            # print("Сформировали новый Json файл с названием фото и типом качества фотографии")
            # print('---------------')

        os.mkdir(r'API vk\VK_photo')
        print('создали временную папку для загрузки фото на Пк : VK_photo ')

        with alive_bar(len(d)) as bar:
            for i in d:
                bar()
                time.sleep(0.1)  
                url = d[i]['url']
                urllib.request.urlretrieve(url, f'API vk\VK_photo\{i}')
                print(f"Записали файл {i} в папку на ПК")
                print('---------------')
        


p = os.path.abspath('data_photo.json')

vk_client = VkUser(token, '5.131') #создаем обьект класса VkUser под именем vk_client с параметрами - личный токен и версия
id = input("Введите Id ВК для поиска фото с аватарок и выгрузки в хранилище Yandex Disk:  ")
vk_client.search_photos(id) #выполняем функцию по поиску аватарок и выгрузке их в память компьютера
Yaid = input('Введите защищенный токен Яндекс диска куда выгрузятся первые 5 фотографий, если фотографий меньше, то вы увидите уведомляющее сообщение:  ')
vk_client.upload_photo(r'API vk\VK_photo') # выгружаем файлы в папку на Яндекс диске . Количество можно поменять ф функции upload_photo
print(f"Ссылка на сформированный Json file:  {p}")

