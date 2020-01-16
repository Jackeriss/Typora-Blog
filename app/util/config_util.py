import copy
import os

import yaml

from app.constant import constant


ENV = os.environ.get("ENV", "dev")
PORT = os.environ.get("PORT", 8000)


def _read_config(env):
    with open(
        os.path.join(constant.BASE_DIR, "config", f"config.{env}.yaml"),
        "r",
        encoding="utf-8",
    ) as stream:
        return yaml.full_load(stream)


if os.path.exists(os.path.join(constant.BASE_DIR, "config", "config.local.yaml")):
    content = _read_config("local")
else:
    content = _read_config(ENV)


class Config:
    _config = content

    @property
    def env(self):
        return ENV

    @property
    def base_dir(self):
        return constant.BASE_DIR

    @property
    def static_path(self):
        return os.path.join(constant.BASE_DIR, "static")

    @property
    def template_path(self):
        return os.path.join(constant.BASE_DIR, "template")

    @property
    def content(self):
        return self._config

    @property
    def server(self):
        self._config["server"]["port"] = PORT
        return self._config["server"]

    @property
    def redis(self):
        conf = copy.deepcopy(self._config["redis"])
        address = (conf.pop("host", "localhost"), conf.pop("port", 6379))
        return address, conf
    
    @property
    def solr(self):
        return self._config["solr"]


config = Config()
