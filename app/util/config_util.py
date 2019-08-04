import argparse
import copy
import os

import yaml

from app.config import const_config


try:
    parser = argparse.ArgumentParser()
    parser.add_argument("--name", type=str)
    parser.add_argument("--env", type=str, default="dev")
    args = parser.parse_args()
    env = args.env
except BaseException as err:
    env = "dev"


def _read_config(_env):
    with open(const_config.BASE_DIR + "/config/config.{}.yaml".format(_env), "r", encoding="utf-8") as stream:
        return yaml.full_load(stream)


if os.path.exists(const_config.BASE_DIR + "/config/config.local.yaml"):
    content = _read_config("local")
else:
    content = _read_config(env)


class Config:
    _config = content

    @property
    def env(self):
        return env

    @property
    def base_dir(self):
        return const_config.BASE_DIR
    
    @property
    def static_path(self):
        return os.path.join(const_config.BASE_DIR, "static")
    
    @property
    def template_path(self):
        return os.path.join(const_config.BASE_DIR, "template")

    @property
    def content(self):
        return self._config

    @property
    def server(self):
        return self._config["server"]

    @property
    def redis(self):
        conf = copy.deepcopy(self._config['redis'])
        address = (conf.pop('host', 'localhost'), conf.pop('port', 6379))
        return address, conf
    
    @property
    def pg(self):
        conf = copy.deepcopy(self._config['pg'])
        address = (conf.pop('host', 'localhost'), conf.pop('port', 6379))
        return address, conf

config = Config()
