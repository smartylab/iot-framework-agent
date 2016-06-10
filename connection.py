import json
import logging

import requests


addr = "http://203.253.23.37:8000/api/context"

logger = logging.getLogger("Connector")
logger.setLevel(logging.INFO)


class Connector(object):

    def __init__(self, user_id, device_addr):
        self.addr = addr
        self.user_id = user_id
        self.device_addr = device_addr
        self.device_item_id = None

    def establish(self):
        try:
            r = requests.get(self.addr, params={
                "user_id": self.user_id,
                "device_addr": self.device_addr
            })

            try:
                r = r.json()
            except Exception as e:
                logger.error("JSON decoding error.")

        except Exception as e:
            logger.error("Transmission error.")

    def transmit(self, data):
        if self.device_item_id is None:
            logger.error("Connection is not established.")
            return
        try:
            requests.post(self.addr, data=json.dumps({
                'device_item_id': self.device_item_id,
                'context': data
            }))
        except Exception as e:
            logger.error("Transmission error.")

