##### WORKING MAIN #####
# UPLOAD_FOLDER  = 'G:\\!TEST\\uploads'
# PROXY_FOLDER = 'G:\\!TEST\\proxy'
# BACKREMOVE_DELETED_PATH = 'G:\\!PORTRETY_DATABASE\\DELETED'

# Пути для РЕН-ТВ (общие пути)
UPLOAD_FOLDER = 'G:\\!TEST'
PROXY_FOLDER = 'G:\\!TEST\\AVATARS'
BACKREMOVE_DELETED_PATH = 'G:\\!TEST\\DELETED'

# Директории для Пятого канала (5TV)
CHANNEL_DIRS = {
    '5TV': ['Z:\\!TEST', 'Z:\\!TEST\\AVATARS', 'Z:\\!TEST\\DELETED']
}

ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}
# Конфигурация для Рен-ТВ
RENTV_EXCEL_FILE = 'Z:\\!TEST\\rentv_data.xlsx'
# Конфигурация для Пятого канала
FTV_EXCEL_FILE = 'G\\!TEST\\5tv_data.xlsx'



# Сопоставление каналов с их именами и Excel-файлами
CHANNELS = {
    'rentv': {
        'name': 'Рен-ТВ',
        'excel': RENTV_EXCEL_FILE
    },
    '5tv': {
        'name': 'Пятый Канал',
        'excel': FTV_EXCEL_FILE
    }
}


# Вспомогательная функция для получения пути в зависимости от канала
def get_channel_path(path_type, channel):
    """
    Возвращает путь в зависимости от канала
    
    :param path_type: тип пути ('upload', 'proxy', 'deleted')
    :param channel: канал ('rentv' или '5tv')
    :return: соответствующий путь для указанного канала
    """
    if channel == 'rentv':
        if path_type == 'upload':
            return UPLOAD_FOLDER
        elif path_type == 'proxy':
            return PROXY_FOLDER
        elif path_type == 'deleted':
            return BACKREMOVE_DELETED_PATH
    elif channel == '5tv':
        if path_type == 'upload':
            return CHANNEL_DIRS['5TV'][0]
        elif path_type == 'proxy':
            return CHANNEL_DIRS['5TV'][1]
        elif path_type == 'deleted':
            return CHANNEL_DIRS['5TV'][2]
    return UPLOAD_FOLDER  # возвращаем путь по умолчанию, если канал не определен
