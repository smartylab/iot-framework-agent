import json
import logging
import unittest

import time
import threading
import requests

import numpy as np
import sys

import settings
import withings_callback
from agent.agent import EHealthKitAgent, SpheroBallAgent, RollingSpiderAgent
from agent.withings_agent import WithingsAgent, MEASTYPE

logging.basicConfig(format="[%(name)s][%(asctime)s] %(message)s", level=logging.INFO)


class EHealthKitAgentTestCase(unittest.TestCase):
    def __init__(self, user_id, device_item_id, addr):
        super(EHealthKitAgentTestCase, self).__init__()
        self.user_id = user_id
        self.device_item_id = device_item_id
        self.addr = addr

    def setUp(self):
        self.logger = logging.getLogger("EHealthKitAgentTestCase")

    def runTest(self):
        time_from = time.time()
        a = EHealthKitAgent(self.user_id, self.device_item_id, self.addr)
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


class SpheroBallAgentTestCase(unittest.TestCase):
    def __init__(self, user_id, device_item_id, addr):
        super(SpheroBallAgentTestCase, self).__init__()
        self.user_id = user_id
        self.device_item_id = device_item_id
        self.addr = addr

    def setUp(self):
        self.user_id = 'mkkim'
        self.password = '1234'
        self.device_item_id = 8

        self.connection_data = {
            "user_id": self.user_id,
            "password": self.password,
            "device_item_id": self.device_item_id
        }
        res = requests.post(settings.CONNECT_API, data=json.dumps(self.connection_data)).json()
        assert res['code'] == 'SUCCESS'
        self.device_item = res['device_item']
        self.device_model = res['device_model']
        self.addr = self.device_item['item_address']
        self.is_running = True
        self.logger = logging.getLogger("SpheroBallAgentTestCase")
        self.logger.setLevel(logging.INFO)

    def tearDown(self):
        res = requests.delete(settings.CONNECT_API, data=json.dumps(self.connection_data)).json()
        self.logger.info(res)

    def runTest(self):
        import pygame
        time_from = time.time()
        a = SpheroBallAgent(addr=self.addr)
        time_to = time.time()
        self.logger.info("Time Taken for Connection: %s (s)" % (time_to - time_from))

        pygame.init()
        screen = pygame.display.set_mode((400,400),0,32)

        screen.fill((250, 250, 250))

        # Display some text
        font = pygame.font.Font(None, 36)
        text = font.render("Sphero Ball Agent", True, (10, 10, 10))
        screen.blit(text, (10, 10))

        h = 50
        textlist = [
            "Forward: <Up Arrow>",
            "Left: <Left Arrow>",
            "Right: <Right Arrow>",
            "Quit: <Q>",
        ]
        font = pygame.font.Font(None, 24)
        for textstr in textlist:
            h += 30
            text = font.render(textstr, True, (10, 10, 10))
            screen.blit(text, (10, h))

        pygame.display.flip()

        keys = pygame.key.get_pressed()
        clock1 = pygame.time.Clock()
        clock2 = pygame.time.Clock()

        while not a.connected:
            time.sleep(1)

        def handle():
            left = 0; right = 0; down = 0; up = 0; angle = 0
            maxcnt = 16; maxspeed = 128; maxangle = 359
            while self.is_running:
                if keys[pygame.K_q]:
                    self.is_running = False
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

                self.logger.debug("SPEED: %s, ANGLE: %s" % (speed, angle))
                a.roll(speed=int(speed), heading=int(angle))

                clock1.tick(16)

        threading.Thread(target=handle).start()

        def transmit():
            while self.is_running:
                context = a.acquire_context()
                time_from = time.time()
                a.transmit(context)
                time_to = time.time()
                self.logger.info("Time Taken for Transmission: %s (s)" % (time_to - time_from))
                clock2.tick(4)

        threading.Thread(target=transmit).start()

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


class RollingSpiderAgentTestCase(unittest.TestCase):
    def __init__(self, user_id, device_item_id, addr):
        super(RollingSpiderAgentTestCase, self).__init__()
        self.user_id = user_id
        self.device_item_id = device_item_id
        self.addr = addr

    def setUp(self):
        self.is_running = True
        self.logger = logging.getLogger("RollingSpiderAgentTestCase")
        self.logger.setLevel(logging.INFO)

    def runTest(self):
        import pygame
        time_from = time.time()
        a = RollingSpiderAgent(addr=self.addr)
        if not a.connected:
            self.logger.error("Cannot connect to the device, %s" % self.device_item)
            return
        time_to = time.time()
        self.logger.info("Time Taken for Connection: %s (s)" % (time_to - time_from))

        pygame.init()
        screen = pygame.display.set_mode((400,400),0,32)

        screen.fill((250, 250, 250))

        # Display some text
        font = pygame.font.Font(None, 36)
        text = font.render("Rolling Spider Agent", True, (10, 10, 10))
        screen.blit(text, (10, 10))

        h = 50
        textlist = [
            "Takeoff: <Enter>",
            "Land: <Space>",
            "Emergency: <Q>",
            "Left: <Left Arrow>",
            "Right: <Right Arrow>",
            "Forward: <Up Arrow>",
            "Backward: <Down Arrow>",
            "Ascend: <A>",
            "Descend: <Z>",
            "Inc. Speed: <.>",
            "Dec. Speed: <,>",
        ]
        font = pygame.font.Font(None, 24)
        for textstr in textlist:
            h += 30
            text = font.render(textstr, True, (10, 10, 10))
            screen.blit(text, (10, h))

        pygame.display.flip()

        clock1 = pygame.time.Clock()
        clock2 = pygame.time.Clock()

        keys = pygame.key.get_pressed()

        def transmit():
            time_from = time.time()
            context = a.acquire_context()
            self.logger.info("Acquired Context: %s" % context)
            a.transmit(context)
            time_to = time.time()
            self.logger.info("Time Taken for Transmission: %s (s)" % (time_to - time_from))

        def handle():
            while self.is_running:

                if keys[pygame.K_LEFT]:
                    self.logger.info("Left")
                    a.turn_left()
                elif keys[pygame.K_RIGHT]:
                    self.logger.info("Right")
                    a.turn_right()

                if keys[pygame.K_UP]:
                    self.logger.info("Up")
                    a.move_fw()
                elif keys[pygame.K_DOWN]:
                    self.logger.info("Down")
                    a.move_bw()

                if keys[pygame.K_z]:
                    self.logger.info("Descend")
                    a.descend()
                elif keys[pygame.K_a]:
                    self.logger.info("Ascend")
                    a.ascend()

                if keys[pygame.K_PERIOD]:
                    self.logger.info("Inc. Speed")
                    a.incr_speed()
                    transmit()
                elif keys[pygame.K_COMMA]:
                    self.logger.info("Dec. Speed")
                    a.decr_speed()
                    transmit()

                clock1.tick(4)

        threading.Thread(target=handle).start()

        while self.is_running:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.is_running = False
                if event.type == pygame.KEYDOWN:
                    keys = pygame.key.get_pressed()

                    if keys[pygame.K_RETURN]:
                        self.logger.info("Takeoff")
                        a.takeoff()
                        transmit()
                    elif keys[pygame.K_SPACE]:
                        self.logger.info("Land")
                        a.land()
                        transmit()
                    elif keys[pygame.K_q]:
                        self.logger.info("Emergency")
                        a.emergency()
                        transmit()
                        self.is_running = False
                        break

                if event.type == pygame.KEYUP:
                    keys = pygame.key.get_pressed()
            clock1.tick(64)

        a.disconnect()
        pygame.quit()


class WithingsAgentTestCase(unittest.TestCase):
    def __init__(self, user_id, device_item_id, key, secret):
        super(WithingsAgentTestCase, self).__init__()
        self.user_id = user_id
        self.device_item_id = device_item_id
        self.key = key
        self.secret = secret

    def setUp(self):
        self.agent_addr = settings.AGENT_ADDR
        self.agent_port = settings.AGENT_PORT

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
