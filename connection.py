import json
import logging

import requests

import settings

logger = logging.getLogger("Connector")
logger.setLevel(logging.INFO)


class Connector(object):

    def __init__(self, user_id, device_addr):
        self.user_id = user_id
        self.device_addr = device_addr
        self.device_item_id = None

    def establish(self):
        pass