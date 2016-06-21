import logging
import threading
import unittest

import time

import withings_callback
from agent.withings_agent import WithingsAgent, MEASTYPE

logging.basicConfig(format="[%(name)s][%(asctime)s] %(message)s", level=logging.INFO)


class WithingsAgentTestCase(unittest.TestCase):

    def setUp(self):
        self.user_id = 'mkkim'
        self.device_item_id = 1
        self.server_addr = "http://203.253.23.20"
        self.logger = logging.getLogger("WithingsAgentTestCase")

    def test(self):
        def start_server():
            withings_callback.run()
        threading.Thread(target=start_server).start()

        a = WithingsAgent(fwk_user_id=self.user_id, device_item_id=self.device_item_id,
                          key="eebf485eb5f98f3df872897de240f14228bf8638177ecf10cd8b5dfc640dd8",
                          secret="b998416e2ef75587388dde664992201773bdf68452224258d12b093ff",
                          server_addr=self.server_addr)
        a.connect()
        while not a.is_authorized:
            time.sleep(1)
        a.acquire(MEASTYPE.pulse)


if __name__ == '__main__':
    unittest.main()
