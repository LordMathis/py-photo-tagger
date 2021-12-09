import os

MODELS_BASE_PATH = os.environ.get('MODELS_BASE_PATH', './models')
DATA_BASE_PATH = os.environ.get('DATA_BASE_PATH', './data')

DB_HOST = os.environ.get('DB_HOST', 'localhost')
DB_PORT = os.environ.get('DB_PORT', 27017)
DB_NAME = os.environ.get('DB_NAME', 'tagger')
