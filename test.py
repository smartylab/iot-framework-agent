import logging
import unittest

import time

import threading

import pygame
import sys
import math

import numpy as np

from agent import EHealthKitAgent, SpheroBallAgent

logging.basicConfig(format="[%(name)s][%(asctime)s] %(message)s")
logger = logging.getLogger("IoT Device Agent")
logger.setLevel(logging.INFO)


@unittest.skip("")
class EHealthKitAgentTestCase(unittest.TestCase):

    def setUp(self):
        self.user_id = 'mkkim'
        self.device_item_id = 1
        self.addr = 'COM18'

    def test_ecg(self):
        time_from = time.time()
        a = EHealthKitAgent(user_id=self.user_id, device_item_id=self.device_item_id, addr=self.addr)
        time_to = time.time()
        logger.info("Time Taken for Connection: %s (s)" % (time_to - time_from))

        time_from = time.time()
        context = a.acquire_meas(EHealthKitAgent.Measurement.ECG)
        time_to = time.time()
        logger.info("Time Taken for Acquisition: %s (s)" % (time_to - time_from))
        logger.info("Acquired Context: %s" % (context))

        time_from = time.time()
        a.transmit(context)
        time_to = time.time()
        logger.info("Time Taken for Transmission: %s (s)" % (time_to - time_from))

    @unittest.skip("")
    def test_ecg_series(self):
        time_from = time.time()
        a = EHealthKitAgent(user_id=self.user_id, device_item_id=self.device_item_id, addr=self.addr)
        time_to = time.time()
        logger.info("Time Taken for Connection: %s (s)" % (time_to-time_from))

        time_from = time.time()
        context = a.acquire_meas(EHealthKitAgent.Measurement.ECG, is_series=True, duration=10)
        time_to = time.time()
        logger.info("Time Taken for Acquisition: %s (s)" % (time_to-time_from))

        time_from = time.time()
        a.transmit(context, is_series=True)
        time_to = time.time()
        logger.info("Time Taken for Transmission: %s (s)" % (time_to-time_from))


# @unittest.skip("")
class SpheroBallTestCase(unittest.TestCase):

    def setUp(self):
        self.user_id = 'mkkim'
        self.device_item_id = 1
        self.addr = "68:86:E7:04:A6:B4",

    def test(self):
        a = SpheroBallAgent(user_id=self.user_id, device_item_id=self.device_item_id, addr=self.addr)

        pygame.init()
        pygame.display.iconify()

        keys = pygame.key.get_pressed()
        clock = pygame.time.Clock()

        # while not a.connected:
        #     time.sleep(1)
        # for _ in range(10):
        #     a.roll()
        #     time.sleep(1)
        # a.disconnect()
        # logger.info("Disconnected.")

        def handle():
            left = 0; right = 0; down = 0; up = 0
            maxcnt = 10; maxspeed = 30
            while True:
                if keys[pygame.K_LEFT]:
                    left = min(left+1, maxcnt)
                    logger.debug('LEFT: %s' % left)
                else:
                    left = max(left-1, 0)

                if keys[pygame.K_RIGHT]:
                    right = min(right+1, maxcnt)
                    logger.debug('RIGHT: %s' % right)
                else:
                    right = max(right-1, 0)

                if keys[pygame.K_UP]:
                    up = min(up+1, maxcnt)
                    logger.debug('UP: %s' % up)
                else:
                    up = max(up-1, 0)

                if keys[pygame.K_DOWN]:
                    down = min(down+1, maxcnt)
                    logger.debug('DOWN: %s' % down)
                else:
                    down = max(down-1, 0)

                speed = maxspeed*np.tanh(abs(up-down)/10)
                if up < down:
                    speed = -speed
                angle = 360*np.tanh(abs(right-left)/10)
                if right < left:
                    angle = -angle

                logger.info("SPEED: %s, ANGLE: %s" % (speed, angle))

                clock.tick(4)

        threading.Thread(target=handle).start()

        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                if event.type == pygame.KEYUP:
                    keys = pygame.key.get_pressed()

        pygame.quit()
        quit()


if __name__ == '__main__':
    unittest.main()
