import json
import logging
import unittest

import time

import threading

import pygame
import sys

import numpy as np
import requests

import settings
from agent.agent import SpheroBallAgent

logging.basicConfig(format="[%(name)s][%(asctime)s] %(message)s")


class SpheroBallAgentTestCase(unittest.TestCase):

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

    def test(self):
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


if __name__ == '__main__':
    unittest.main()
