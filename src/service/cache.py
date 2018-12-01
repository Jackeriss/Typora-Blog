import json
import copy
import logging

from src.util.html2template import html2template
from src.config import Config

class Cache:
    def __init__(self):
        self.posts = []

    def load(self):
        self.posts = html2template()

cache = Cache()
