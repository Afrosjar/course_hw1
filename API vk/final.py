
import requests
from pprint import pprint
import os
import yadisk
from datetime import datetime
import json
from alive_progress import alive_bar
import time


class Yandex_User():
    def __init__(self, TOKEN):
        self.token = TOKEN
        self.URL = 'https://cloud-api.yandex.net/v1/disk/resources'
        self.headers = {'Content-Type': 'application/json', 'Accept': 'application/json', 'Authorization': f'OAuth {TOKEN}'}
        self.uploader = yadisk.YaDisk(token = self.token)

    def create_folder_on_Yandex_Disk(self,name):
        """Создание папки. \n path: Путь к создаваемой папке."""
        requests.put(f'{self.URL}?path={name}',headers = self.headers)
        print('Создали папку "Import Photo From VK" на вашем яндекс диске')
    
    def upload_from_URL_to_Yandex(self, download_count=5):
        """Загрузка фото по заданному URL на Яндекс диск."""
        if self.uploader.check_token(): # Если вернет True - работаем дальше, иначе ошибка авторизации 
            print("Запрос выполнен успешно")
            with alive_bar(download_count) as bar:  
                count = 0    
                with open(os.path.abspath('dict_name_and_URL.json')) as f:
                    photo = json.load(f)
                    for name in photo:
                        if self.uploader.is_file(f'/Import Photo From VK/{name}'):       
                            self.uploader.remove(f'/Import Photo From VK/{name}',permanently = True)
                            print(f"Предыдущий файл с названием {name} был удалён.")
                            print('------------------------------')
                            self.uploader.upload_url(f'{photo[name]["url"]}', f'/Import Photo From VK/{name}')
                            print(f'Файл {name} загружен')
                            print('------------------------------')
                            bar()
                            time.sleep(0.5) 
                            count +=1
                                
                                
                        else:
                            self.uploader.upload_url(f'{photo[name]["url"]}', f'/Import Photo From VK/{name}')
                            print(f'Файл {name} загружен')
                            print('------------------------------')
                            bar()
                            count+=1
                            time.sleep(0.5) 
                            count +=1        
            if count < download_count:
                print(f'Всего в папке было файлов : {count}, поэтому записали файлов: {count} , а не {download_count}')
        else:
            print('Ошибка авторицазии, перезапустите программу и введите верный токен')
            exit()
        os.remove(r'dict_name_and_URL.json')
        print(f'Ссылка на обновленный Яндекс диск : {r"https://disk.yandex.ru/client/disk/Import%20Photo%20From%20VK"}')
        print(f"Ссылка на сформированный Json file:  {os.path.abspath('data_photo.json')}") 
    
class VkUser:
    url = 'https://api.vk.com/method/'
    

    def __init__(self, token, version):
        self.params = {
            'access_token': token,
            'v': version
        }

                    
    def upload_from_vk_to_PC(self,owner_id):
        search_photos_url=self.url+'photos.get'
        search_photos_params ={
            'owner_id': owner_id,
            'album_id':'profile',
            'extended' : '1',
            'count':5 # тут могу принять количество из дополнительного аргумента функции, чтобы можно было выгружать не 5 , а любое количество
            }
     
        res = requests.get(search_photos_url,params={**self.params, **search_photos_params})
        if res.ok :
            print(f"Запрос прошел, ответ сервера: {res.status_code}")
        else:
            print(f'Сервер не отдает информацию, возможно ошибка введенных данных или ошибка со стороны сервера , код ошибки : {res.status_code}')
        try:
            data = res.json()['response']['items']
        except KeyError:
            print(f'В запросе ошибка, Токен или ID Пользователя не корректны, проверьте и введите заново') # Проверка запроса статус кодом, если не отдает информацию по res[]
            exit()

        # проверка дублируется, так как даже с неверными ID и Token сервер может дать ответ 200, поэтому проверяем отдает ли ВК информацию по полям

        dict_names_and_url = {} # Создаем словарь где ключи - Имена, а значения размер фото и ссылка на фото, достаем самые большие значения размеров фото 
        for photo in data:
            key = f"{photo['likes']['count']}.jpg"
            if key not in dict_names_and_url.keys():
                key = f"{photo['likes']['count']}.jpg"
            else:
                key = f"{photo['likes']['count']}_date_{(datetime.utcfromtimestamp(photo['date']).strftime('%d-%m-%Y_%H-%M-%S'))}.jpg"

            max_size = 0
            for size in photo['sizes']:
                    if size['height'] > 0:
                        if size['height'] > max_size:
                            dict_names_and_url[key] = {'url':size['url'],'type':size['type']}
                            max_size = size['height']                            
                    else:
                        dict_names_and_url[key] = {'url':photo['sizes'][-1]['url'],'type':photo['sizes'][-1]['type']}
                        
            
        
        json_dict = [{"file_name":photo, "type":dict_names_and_url[photo]["type"] } for photo in dict_names_and_url ]


        with open ('dict_name_and_URL.json', 'w') as file: # создаем временный json файл с полученным словарем ( имя файла - url - тип)
            json.dump(dict_names_and_url, file)

        with open("data_photo.json", "w") as file: 
            json.dump(json_dict, file)


vk_client = VkUser(input("Введите защищенный токен ВК: "), '5.131') #создаем обьект класса VkUser под именем vk_client с параметрами - личный токен и версия

vk_client.upload_from_vk_to_PC(input('Введите ID пользователя Вконтакте: ')) # Выполняем функцию по поиску аватарок и выгрузке их в память компьютера 

ya_user = Yandex_User(input('Введите защищенный Токен с Яндекс полигона: ')) #создаем обьект класса Yandex_User под именем ya_user токен 

ya_user.create_folder_on_Yandex_Disk('Import Photo From VK') # Создаем папку на Яндекс диске для последующей выгрузки фотографий

ya_user.upload_from_URL_to_Yandex()


