from flask import Flask, request, send_from_directory, send_file, Response
import logging
# импортируем создаем класс изображений
from models.plate_reader import PlateReader
# чтобы сразу считать файл не сохранять на диск
import io
from PIL import UnidentifiedImageError
from check_errors import check_format, check_file_exists, check_images_num

# задаем папку с изображениями
IMAGE_FOLDER = 'images/'
app = Flask(__name__)
app.config['IMAGE_FOLDER'] = IMAGE_FOLDER

# тут создаем класс изображений
plate_reader = PlateReader.\
            load_from_file('/app/model_weights/plate_reader_model.pth')


# это ручка/хендлер. Указываем, что это пост запрос (посылаем данные)
@app.route('/read_plate', methods=['POST'])
def read_plate():
    # получаем сырые данные/картинку
    im = request.get_data()

    logging.info(f"DBG >>>>>>>>> {im}")
    im = io.BytesIO(im)
    # если с изображением что-то не так, возвращаем ошибку
    try:
        res = plate_reader.read_text(im)
    except UnidentifiedImageError as e:
        return {
            'error': 'invalid image format'
        }, 400

    return {
        'plate_number': res,
    }


@app.route('/read_plate/id', methods=['POST'])
def read_plate_image():
    # получаем сырые данные/картинку из сервиса. Использовать requests
    im = get_image(im_id)
    im = io.BytesIO(im)
    # если с изображением что-то не так, возвращаем ошибку
    try:
        res = plate_reader.read_text(im)
    except UnidentifiedImageError as e:
        return {
            'error': 'invalid image format'
        }, 400

    return {
        'plate_number': res,
    }


@app.route('/greeting')
def hello():
    return '<h1><center>Hello!!!!!</center></h1>'


@app.route('/func')
def hello_2():
    return '<h1><center>Here is func</center></h1>'


@app.route('/json')
def hello_json():
    return {
        "key": "Oleg",
        "key2": 1,
    }


@app.route('/args')
def hello_args():
    # получить доступ к request inc с распаршенными данными из
    # хедеров
    # http://localhost:8080/args?name=Artem
    # http://localhost:8080/<param_name>
    name = request.args.get('name', 'Oleg')
    return {
        "key": f"Hello {name}",
        "key2": 1,
    }


@app.route('/args2/<name>')
def hello_args_2(name: str):
    # http://localhost:8080/args2/Artem
    return {
        "key": f"Hello {name}",
        "key2": 1,
    }


@app.route('/images/<image_ids>')
def image_handler(image_ids: str):
    # получаем список id изображений
    image_id_list = image_ids.split(',')
    images = []
    # проверяем, что изображений 1 или 2
    if not check_images_num(image_id_list):
        return {
                'error': 'Too many images, provide only 2'
               }, 404
    # если все ок, то обрабатываем изображения
    for image_id in image_id_list:
        path = app.config['IMAGE_FOLDER'] + str(image_id)

        # проверяем, что ок с форматом
        if check_format(path) == 0:
            return {
                'error': 'Wrong file format'
            }, 400
        elif check_format(path) == 1:
            path += '.jpg'
        # логируем
        logging.info(f"DBG >>>>>>>>> {path}")

        # проверяем, что изображения существуют
        if check_file_exists(path):
            with open(path, 'rb') as file:
                data = file.read()
            images.append(data)
        else:
            return {
                'error': 'File not found'
            }, 404
    # если изображений 2, то посылаем байтовое представление двух изображений
    if len(images) == 2:
        return Response(
                io.BytesIO(b'__'.join(images)),
                mimetype='multipart/x-mixed-replace'
        )
    # если изображение 1, то посылаем байтовое представление одного изображения
    elif len(images) == 1:
        return Response(images[0], mimetype='image/jpeg')
    # иначе ошибка
    else:
        return {
            'error': 'Invalid number of images'
        }, 400


if __name__ == '__main__':
    logging.basicConfig(
        format='[%(levelname)s] [%(asctime)s] %(message)s',
        level=logging.INFO,
    )

    # localhost <- фейковый адрес локального компа, который
    # доступен только из машины
    # 127.0.0.1 <- это запуск тоьлько на компьютере
    # 0.0.0.0 <- этот сервис мб доступен извне машины

    app.json.ensure_ascii = False  # чтобы норм работала кириллица
    # порт исправлен на 7777, так как в задании 7777
    app.run(host='0.0.0.0', port=7777, debug=True)
