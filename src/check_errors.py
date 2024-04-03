import os


def check_format(path):
    '''
    проверка на формат изображения
    '''
    if '.' in path:
        if path[-4:] != '.jpg':
            return 0
        else:
            return 2
    return 1


def check_file_exists(path):
    '''
    проверка на существование изображения
    '''
    if os.path.exists(path):
        return 1
    return 0


def check_images_num(images_list):
    '''
    проверка на то, что подано не больше 2х изображений
    '''
    if len(images_list) > 2:
        return 0
    return 1
