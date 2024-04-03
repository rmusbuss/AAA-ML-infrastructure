import time
import requests
import io
from typing import Union


class PlateClient:
    def __init__(self, addr: str):
        self.addr = addr

    def read_plate_number(self, im: bytes) -> str:
        '''
        Функция, которая принимает на вход изображение в байтовом виде
        и передает ее в ML сервис.
        Возвращает ответ из ML сервиса или печатает сообщение об ошибке
        '''
        # сообщение об ошибке, если думает больше 1 сек таймаут
        # try except ReadTimeout ошибка 500 или retry_limit = 5
        retry_limit = 5
        while retry_limit > 0:
            try:
                # отправляем картинку в ML сервис
                res = requests.post(
                    f'http://{self.addr}/read_plate',
                    data=im,  # куда передаем байтики
                    headers={'Content-Type':  # правильный формат для картинки
                             'application/x-www-form-urlencoded'},
                    timeout=1  # 1000 миллисекунд
                )
                # получаем статус ответа
                status = res.status_code
                # в зависимости от статуса выводим ошибку или сам ответ
                if status // 100 == 2:
                    return res.json()['plate_number']
                elif status // 100 == 5:
                    retry_limit -= 1
                    time.sleep(0.1)
                    continue
                elif status // 100 == 4:
                    retry_limit = 0
                    print('Wrong Picture')
            except requests.exceptions.Timeout:
                # если ML сервис долго думает, то показываем эту ошибку
                print('ML Service Doesnt Respond')
                print(f'Retrying {6 - retry_limit} time')
                retry_limit -= 1
                time.sleep(0.5)
        return 'ML Model Timeout Error'

    def ask_for_picture(self, external_service_addr: str,
                        image_id: Union[int, str]) -> bytes:
        '''
        Функция, которая на вход принимает адрес внешнего сервиса и
        id изображений
        Выводит картинки в байтовом виде, переданные от сервиса.
        Или принтуют ошибку
        '''
        # задаем кол-во попыток переподключения к внешнему серверу
        retry_limit = 5
        while retry_limit > 0:
            # адрес внешнего сервиса
            pic_url = f'{external_service_addr}{image_id}'
            # пишет try except для таймаута или retry_limit = 5
            try:
                response = requests.get(pic_url,
                                        timeout=1)
                # Проверяем, что запрос выполнен успешно
                if response.status_code // 100 == 2:
                    # Разделяем содержимое ответа на части
                    # Внешний сервис передает две картинки
                    # в байтовом виде, разделенные __
                    parts = response.content.split(b'__')

                    # Создаем список для хранения байтовых
                    # представлений изображений
                    image_data_list = []

                    # Обрабатываем каждую часть
                    for part in parts:
                        # Добавляем байтовое представление изображения в список
                        image_data_list.append(part)

                    # Проверяем, что получены два байтовых
                    # представления изображений
                    if len(image_data_list) == 2:
                        # Получаем байтовые представления изображений
                        image_data1 = image_data_list[0]
                        image_data2 = image_data_list[1]

                        return image_data1, image_data2
                    else:
                        return [image_data_list[0]]
                elif response.status_code // 100 == 5:
                    # если ошибка сервера, то делаем еще одну попытку запроса
                    retry_limit -= 1
                    time.sleep(0.1)
                    continue
                elif response.status_code // 100 == 4:
                    # если ошибка со стороны клиента, то выводим эту ошибку
                    retry_limit = 0
                    error_message = response.json()['error']
                    print(error_message)
                    return False
            except requests.exceptions.Timeout:
                # если внешний сервис долго думает, то показываем эту ошибку
                print('External Picture Service Doesnt Respond')
                print(f'Retrying {6 - retry_limit} time')
                retry_limit -= 1
                time.sleep(0.5)
                # return False
        print('External Picture Service Timeout Error')
        return False


# разные варианты команд и что должно быть выведено
# image_id = '9965.txt'  # wrong file format
# image_id = '996556'  # file not found
# image_id = '996556, 10022'  # file not found
# image_id = '9965.txt, 10022'  # wrong file format
# image_id = '9965,10022,123'  # too many images
# image_id = 9965  # ok
# image_id = 10022  # ok
# image_id = '9965,10022'  # ok
# image_id = '10022,9965'  # ok

# инициализируем клиента
client = PlateClient('127.0.0.1:7777')
# обращаемся к внешнему сервису за картинкой
server_addr = 'http://178.154.222.88:7777/images/'
response = client.ask_for_picture(server_addr, image_id)

# если пришел положительный ответ
# (фотография в байтовом коде, то передаем ее в ML сервис)
if response is not False:
    for file in response:
        res = client.read_plate_number(file)
        print(res)
