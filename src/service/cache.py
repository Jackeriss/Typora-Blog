import json
import copy

from src.util.html2template import html2template
from src.service.log import logger
from src.config import Config

class Cache:
    def __init__(self):
        self.posts = []

    def load(self):
        self.posts = html2template()

cache = Cache()
