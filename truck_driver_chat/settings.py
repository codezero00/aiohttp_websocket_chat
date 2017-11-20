import logging

from envparse import env
import os

ENVFILE_PATH = '.env'

if os.path.isfile(ENVFILE_PATH):
    env.read_envfile(ENVFILE_PATH)
SECRET_KEY = b'0123456789ABCDEF0123456789ABCDEF'
DEBUG = env.bool('DEBUG', default=False)
# network
SITE_HOST = env.str('HOST', default='127.0.0.1')
SITE_PORT = env.int('PORT', default=8088)
# db
DB_HOST = env.str('DB_HOST', default="127.0.0.1")
DB_NAME = env.str('DB_NAME', default="chat_app")
DB_USER = env.str('DB_USER', default="chat_app")
DB_SECRET = env.str('DB_SECRET')
# redis
REDIS_DB_N = env.int('REDIS_DB_N')
REDIS_HOST = env.str('REDIS_HOST', default='localhost')
REDIS_PORT = env.int('REDIS_PORT', default=6379)
# auth
SALT = env.str('SALT')


def get_logger(name):
    level = logging.DEBUG if DEBUG else logging.INFO
    logger = logging.getLogger(name)
    logger.setLevel(level)
    f = logging.Formatter('[L:%(lineno)d]# %(levelname)-8s [%(asctime)s]  %(message)s', datefmt='%d-%m-%Y %H:%M:%S')
    ch = logging.StreamHandler()
    ch.setLevel(level)
    ch.setFormatter(f)
    logger.addHandler(ch)

    return logger
