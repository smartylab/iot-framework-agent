import logging
import unittest

import time

import threading

import pygame
import sys
import math

import numpy as np

from agent import EHealthKitAgent, SpheroBallAgent, RollingSpiderAgent

logging.basicConfig(format="[%(name)s][%(asctime)s] %(message)s")


@unittest.skip("")
class EHealthKitAgentTestCase(unittest.TestCase):

    def setUp(self):
        self.user_id = 'mkkim'
        self.device_item_id = 1
        self.addr = 'COM18'
        self.logger = logging.getLogger("EHealthKitAgent Testing")
        self.logger.setLevel(logging.INFO)

    def test_ecg(self):
        time_from = time.time()
        a = EHealthKitAgent(user_id=self.user_id, device_item_id=self.device_item_id, addr=self.addr)
        time_to = time.time()
        self.logger.info("Time Taken for Connection: %s (s)" % (time_to - time_from))

        time_from = time.time()
        context = a.acquire_context(EHealthKitAgent.Measurement.ECG)
        time_to = time.time()
        self.logger.info("Time Taken for Acquisition: %s (s)" % (time_to - time_from))
        self.logger.info("Acquired Context: %s" % (context))

        time_from = time.time()
        a.transmit(context)
        time_to = time.time()
        self.logger.info("Time Taken for Transmission: %s (s)" % (time_to - time_from))

    @unittest.skip("")
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


# @unittest.skip("")
class SpheroBallTestCase(unittest.TestCase):

    def setUp(self):
        self.user_id = 'mkkim'
        self.device_item_id = 1
        self.addr = "68:86:E7:04:A6:B4"
        self.is_running = True
        self.logger = logging.getLogger("SpheroBallAgent Testing")
        self.logger.setLevel(logging.INFO)

    def test(self):
        a = SpheroBallAgent(user_id=self.user_id, device_item_id=self.device_item_id, addr=self.addr)

        pygame.init()
        canvas = pygame.display.set_mode((400,400),0,32)
        canvas.fill((128,128,128))
        pygame.display.update()

        keys = pygame.key.get_pressed()
        clock = pygame.time.Clock()

        while not a.connected:
            time.sleep(1)

        def handle():
            left = 0; right = 0; down = 0; up = 0; angle = 0
            maxcnt = 128; maxspeed = 128; maxangle = 359
            while self.is_running:
                if keys[pygame.K_q]:
                    self.is_running = False
                    a.disconnect()
                    self.logger.info("Disconnected.")

                if keys[pygame.K_LEFT]:
                    left = min(left+1, maxcnt)
                    self.logger.debug('LEFT: %s' % left)
                else:
                    left = max(int(left/4), 0)

                if keys[pygame.K_RIGHT]:
                    right = min(right+1, maxcnt)
                    self.logger.debug('RIGHT: %s' % right)
                else:
                    right = max(int(right/4), 0)

                if keys[pygame.K_UP]:
                    up = min(up+1, maxcnt)
                    self.logger.debug('UP: %s' % up)
                else:
                    up = max(int(up/4), 0)

                speed = maxspeed*np.tanh(up/16)
                anglechange = (maxangle/10)*np.tanh((right-left)/16)
                angle = angle+anglechange
                if angle < 0:
                    angle = maxangle+angle
                if angle > maxangle:
                    angle = angle-maxangle

                self.logger.info("SPEED: %s, ANGLE: %s" % (speed, angle))
                a.roll(speed=int(speed), heading=int(angle))

                clock.tick(16)

        threading.Thread(target=handle).start()

        def transmit():
            while self.is_running:
                a.transmit(a.acquire_context())
                clock.tick(4)


        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    sys.exit(0)
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()
                if event.type == pygame.KEYUP:
                    keys = pygame.key.get_pressed()

        a.disconnect()
        pygame.quit()
        self.logger.info("Disconnected.")


@unittest.skip("")
class RollingSpiderTestCase(unittest.TestCase):

    def setUp(self):
        self.user_id = 'mkkim'
        self.device_item_id = 1
        self.addr = "E0:14:9F:34:3D:4F"
        self.is_running = True

    def test(self):
        a = RollingSpiderAgent(user_id=self.user_id, device_item_id=self.device_item_id, addr=self.addr)

        pygame.init()
        pygame.display.iconify()

        keys = pygame.key.get_pressed()
        clock = pygame.time.Clock()

        def handle():
            while self.is_running:
                if keys[pygame.K_KP_ENTER]:
                    a.takeoff()
                elif keys[pygame.K_SPACE]:
                    a.land()
                    self.is_running = False
                    break
                elif keys[pygame.K_q]:
                    a.emergency()
                    self.is_running = False
                    break

                if keys[pygame.K_LEFT]:
                    a.turn_left()
                elif keys[pygame.K_RIGHT]:
                    a.turn_right()

                if keys[pygame.K_UP]:
                    a.ascend()
                elif keys[pygame.K_DOWN]:
                    a.descend()

                if keys[pygame.K_PERIOD]:
                    a.incr_speed()
                elif keys[pygame.K_COMMA]:
                    a.decr_speed()

                self.logger.info(a.get_speed())
                clock.tick(4)

        threading.Thread(target=handle).start()

        while self.is_running:
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
