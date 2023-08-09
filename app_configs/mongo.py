from app_configs.common import APP_MODE_PROD, APP_MODE, CREDENTIALS

ALLOW_DISK_USE = True
if APP_MODE == APP_MODE_PROD:
<<<<<<< HEAD
    DB_HOST_MONGO = '127.0.0.1'
=======
    DB_HOST_MONGO = '192.168.100.20'
>>>>>>> master
    DB_PORT_MONGO = 27017
else:
    DB_HOST_MONGO = '127.0.0.1'
    DB_PORT_MONGO = 27017

ALLOW_DISK_USE = True

CREDENTIAL_MONGO = CREDENTIALS['mongo']
DBNAME_MONGO = 'quora_data'
COLLECTION_NAME_SCRAPED_DATA = 'scraped_data'
<<<<<<< HEAD
COLLECTION_NAME_SCRAPED_DATA_DUPLICATED = 'scraped_data_duplicated'
=======
COLLECTION_NAME_SCRAPED_DATA_DUPLICATED = 'scraped_data_duplicated'
>>>>>>> master
