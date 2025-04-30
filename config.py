##### WORKING MAIN #####
# UPLOAD_FOLDER  = 'G:\\!TEST\\uploads'
# PROXY_FOLDER = 'G:\\!TEST\\proxy'
# BACKREMOVE_DELETED_PATH = 'G:\\!PORTRETY_DATABASE\\DELETED'
ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg', 'gif'}

# Конфигурация для Рен-ТВ
RENTV_EXCEL_FILE = '!TEST/rentv_data.xlsx'

# Конфигурация для Пятого канала
FTV_EXCEL_FILE = '!TEST/5tv_data.xlsx'

# Общая конфигурация
UPLOAD_FOLDER  = '!TEST'
PROXY_FOLDER = '!TEST/AVATARS'
BACKREMOVE_DELETED_PATH = '!TEST/DELETED'

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