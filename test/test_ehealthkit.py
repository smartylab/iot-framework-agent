import logging
import unittest

import time


from agent.agent import EHealthKitAgent

logging.basicConfig(format="[%(name)s][%(asctime)s] %(message)s", level=logging.INFO)


class EHealthKitAgentTestCase(unittest.TestCase):

    def setUp(self):
        self.user_id = 'mkkim'
        self.device_item_id = 1
        self.addr = 'COM18'
        self.logger = logging.getLogger("EHealthKitAgentTestCase")

    def test_ecg(self):
        time_from = time.time()
        a = EHealthKitAgent(user_id=self.user_id, device_item_id=self.device_item_id, addr=self.addr)
        time_to = time.time()
        self.logger.info("Time Taken for Connection: %s (s)" % (time_to - time_from))

        time_from = time.time()
        context = a.acquire_context(EHealthKitAgent.Measurement.ECG, is_series=True, duration=3)
        # context = a.acquire_context(EHealthKitAgent.Measurement.ECG)
        time_to = time.time()
        self.logger.info("Time Taken for Acquisition: %s (s)" % (time_to - time_from))
        self.logger.info("Acquired Context: %s" % context)

        time_from = time.time()
        a.transmit(context, is_series=True)
        time_to = time.time()
        self.logger.info("Time Taken for Transmission: %s (s)" % (time_to - time_from))

    def test_ecg_series(self):
        time_from = time.time()
        a = EHealthKitAgent(user_id=self.user_id, device_item_id=self.device_item_id, addr=self.addr)
        time_to = time.time()
        self.logger.info("Time Taken for Connection: %s (s)" % (time_to-time_from))

        time_from = time.time()
        context = a.acquire_context(EHealthKitAgent.Measurement.ECG, is_series=True, duration=10)
        time_to = time.time()
        self.logger.info("Time Taken for Acquisition: %s (s)" % (time_to-time_from))

        time_from = time.time()
        a.transmit(context, is_series=True)
        time_to = time.time()
        self.logger.info("Time Taken for Transmission: %s (s)" % (time_to-time_from))


if __name__ == '__main__':
    unittest.main()