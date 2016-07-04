import json
import logging
import threading
import unittest

import time

import requests

import settings
import withings_callback
from agent.withings_agent import WithingsAgent, MEASTYPE

logging.basicConfig(format="[%(name)s][%(asctime)s] %(message)s", level=logging.INFO)


class WithingsAgentTestCase(unittest.TestCase):

    def setUp(self):
        self.agent_addr = settings.AGENT_ADDR
        self.agent_port = settings.AGENT_PORT
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

        self.server = threading.Thread(target=withings_callback.run)
        self.server.start()

    def tearDown(self):
        res = requests.delete(settings.CONNECT_API, data=json.dumps(self.connection_data)).json()
        self.logger.info(res)
        requests.post('%s:%s/kill' % (self.agent_addr, self.agent_port))
        self.server.join()

    def test(self):
        a = WithingsAgent(key=self.key,
                          secret=self.secret,
                          server_addr=self.agent_addr,
                          server_port=self.agent_port)
        a.connect()
        while not a.is_authorized:
            time.sleep(1)
        contexts = a.acquire(MEASTYPE.pulse)
        for context in contexts:
            self.logger.info("Context: %s" % context)
            time_from = time.time()
            a.transmit(context)
            time_to = time.time()
            self.logger.info("Time Taken for Transmission: %s (s)" % (time_to - time_from))

if __name__ == '__main__':
    unittest.main()
