import os
import logging

ROOT_PATH = os.path.dirname(__file__)


class BaseConfig:
    ROOT_PATH = ROOT_PATH
    PAGE_LIMIT = 5


class DevConfig(BaseConfig):
    ENV = 'dev'
    LOG_LEVEL = logging.DEBUG
    SETTING = {
        'template_path': os.path.join(ROOT_PATH, 'template'),
        'static_path': os.path.join(ROOT_PATH, 'static'),
        'debug': True,
        'gzip': True,
        'cookie_secret': 'oqA/6vVxSu6IU+3UErK21/yv7XHASUwap+0z6WL3TJQ=',
    }


class ProdConfig(BaseConfig):
    ENV = 'prod'
    LOG_LEVEL = logging.WARNING
    SETTING = {
        'template_path': os.path.join(ROOT_PATH, 'template'),
        'static_path': os.path.join(ROOT_PATH, 'static'),
        'debug': False,
        'gzip': True,
        'cookie_secret': 'oqA/6vVxSu6IU+3UErK21/yv7XHASUwap+0z6WL3TJQ=',
    }
    

assert set(DevConfig.__dict__.keys()) - set(ProdConfig.__dict__.keys()) == set(), 'dev config has more keys than prod config !'

current_env = os.environ.get('ENV')
if current_env == 'prod':
    Config = ProdConfig
else:
    Config = DevConfig
