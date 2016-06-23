import json
import logging
import threading
import unittest

import time

import multiprocessing
import requests

import settings
import withings_callback
from agent.withings_agent import WithingsAgent, MEASTYPE

logging.basicConfig(format="[%(name)s][%(asctime)s] %(message)s", level=logging.INFO)


class WithingsAgentTestCase(unittest.TestCase):

    def setUp(self):
        self.server_addr = "http://203.253.23.40"
        self.user_id = 'mkkim'
        self.password = '1234'
        self.device_item_id = 10

        self.connection_data = {
            "user_id": self.user_id,
            "password": self.password,
            "device_item_id": self.device_item_id
        }
        res = requests.post(settings.CONNECT_API, data=json.dumps(self.connection_data)).json()
        assert res['code'] == 'SUCCESS'
        self.device_item = res['device_item']
        self.device_model = res['device_model']
        self.key, self.secret = self.device_item['item_address'].split('/')
        self.logger = logging.getLogger("WithingsAgentTestCase")

        self.server = multiprocessing.Process(target=withings_callback.app.run)
        self.server.start()

    def tearDown(self):
        res = requests.delete(settings.CONNECT_API, data=json.dumps(self.connection_data)).json()
        self.logger.info(res)
        if self.server is not None:
            self.server.terminate()
            self.server.join()

    def test(self):
        a = WithingsAgent(fwk_user_id=self.user_id, device_item_id=self.device_item_id,
                          key=self.key,
                          secret=self.secret,
                          server_addr=self.server_addr)
        a.connect()
        while not a.is_authorized:
            time.sleep(1)
        a.acquire(MEASTYPE.pulse)


if __name__ == '__main__':
    unittest.main()
