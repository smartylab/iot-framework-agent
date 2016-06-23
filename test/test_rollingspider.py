import json
import logging
import unittest

import time

import threading

import pygame
import sys

import requests

import settings
from agent.agent import RollingSpiderAgent

logging.basicConfig(format="[%(name)s][%(asctime)s] %(message)s")


class RollingSpiderAgentTestCase(unittest.TestCase):

    def setUp(self):
        self.user_id = 'mkkim'
        self.password = '1234'
        self.device_item_id = 7

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
        self.logger = logging.getLogger("RollingSpiderAgentTestCase")
        self.logger.setLevel(logging.INFO)

    def tearDown(self):
        requests.delete(settings.CONNECT_API, data=json.dumps(self.connection_data)).json()

    def test(self):
        time_from = time.time()
        a = RollingSpiderAgent(user_id=self.user_id, device_item_id=self.device_item_id, addr=self.addr)
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
            self.logger.info("Time Taken for Acquisition and Transmission: %s (s)" % (time_to - time_from))

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
                    sys.exit(0)
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


if __name__ == '__main__':
    unittest.main()
