
import requests
import os
import yadisk
from datetime import datetime
import json
import time
from tqdm import tqdm


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
    
    def upload_from_URL_to_Yandex(self):
        """Загрузка фото по заданному URL на Яндекс диск."""

        if self.uploader.check_token(): # Если вернет True - работаем дальше, иначе ошибка авторизации 
            print("Запрос выполнен успешно")
        else:
            print('Ошибка авторицазии, перезапустите программу и введите верный токен')
            exit() 

        with open(os.path.abspath('dict_name_and_URL.json')) as f:
            photo = json.load(f)

            for name in tqdm(photo, desc='Total'):
                if self.uploader.is_file(f'/Import Photo From VK/{name}'):       
                    self.uploader.remove(f'/Import Photo From VK/{name}',permanently = True)
                    tqdm.write(f"Предыдущий файл с названием {name} был удалён.")
                    tqdm.write('------------------------------')
                    self.uploader.upload_url(f'{photo[name]["url"]}', f'/Import Photo From VK/{name}')
                    tqdm.write(f'Файл {name} загружен')
                    tqdm.write('------------------------------')
                    time.sleep(0.5) 
                                
                                
                else:
                    self.uploader.upload_url(f'{photo[name]["url"]}', f'/Import Photo From VK/{name}')
                    tqdm.write(f'Файл {name} загружен')
                    tqdm.write('------------------------------')

                    time.sleep(0.5)      

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

                    
    def upload_from_vk_to_PC(self,owner_id, photo_count):
        search_photos_url = self.url+'photos.get'
    def get_photo_URL(self,owner_id):
        search_photos_url=self.url+'photos.get'
        search_photos_params ={
            'owner_id': owner_id,
            'album_id':'profile',
            'extended' : '1',
            'count':photo_count 
            }
     
        res = requests.get(search_photos_url,params={**self.params, **search_photos_params})
        if res.ok :
            print(f"Запрос прошел, ответ сервера: {res.status_code}")
        else:
            print(f'Сервер не отдает информацию, возможно ошибка введенных данных или ошибка со стороны сервера , код ошибки : {res.status_code}')
            exit()
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
        return dict_names_and_url


vk_client = VkUser(input("Введите защищенный токен ВК: "), '5.131') #создаем обьект класса VkUser под именем vk_client с параметрами - личный токен и версия

vk_client.upload_from_vk_to_PC(input('Введите ID пользователя Вконтакте: '),input('Введите количество желаемых фотографий для выгрузки :')
) # Выполняем функцию по поиску аватарок и выгрузке их в память компьютера 

ya_user = Yandex_User(input('Введите защищенный Токен с Яндекс полигона: ')) #создаем обьект класса Yandex_User под именем ya_user токен 

ya_user.create_folder_on_Yandex_Disk('Import Photo From VK') # Создаем папку на Яндекс диске для последующей выгрузки фотографий

ya_user.upload_from_URL_to_Yandex()



