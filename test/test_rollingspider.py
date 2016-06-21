import logging
import unittest

import time

import threading

import pygame
import sys


from agent.agent import RollingSpiderAgent

logging.basicConfig(format="[%(name)s][%(asctime)s] %(message)s")


class RollingSpiderAgentTestCase(unittest.TestCase):

    def setUp(self):
        self.user_id = 'mkkim'
        self.device_item_id = 1
        self.addr = "E0:14:9F:34:3D:4F"
        self.is_running = True
        self.logger = logging.getLogger("RollingSpiderAgentTestCase")
        self.logger.setLevel(logging.INFO)

    def test(self):
        a = RollingSpiderAgent(user_id=self.user_id, device_item_id=self.device_item_id, addr=self.addr)

        pygame.init()
        canvas = pygame.display.set_mode((400,400),0,32)
        canvas.fill((128,128,128))
        pygame.display.update()

        clock1 = pygame.time.Clock()
        clock2 = pygame.time.Clock()

        keys = pygame.key.get_pressed()

        def handle():
            while self.is_running:

                if keys[pygame.K_LEFT]:
                    a.turn_left()
                elif keys[pygame.K_RIGHT]:
                    a.turn_right()

                if keys[pygame.K_UP]:
                    a.move_fw()
                elif keys[pygame.K_DOWN]:
                    a.move_bw()

                if keys[pygame.K_z]:
                    a.descend()
                elif keys[pygame.K_x]:
                    a.ascend()

                if keys[pygame.K_PERIOD]:
                    a.incr_speed()
                elif keys[pygame.K_COMMA]:
                    a.decr_speed()

                clock1.tick(16)

        threading.Thread(target=handle).start()

        def transmit():
            while self.is_running:
                time_from = time.time()
                a.transmit(a.acquire_context())
                time_to = time.time()
                self.logger.info("Time Taken for Acquisition and Transmission: %s (s)" % (time_to - time_from))
                clock2.tick(4)

        threading.Thread(target=transmit).start()

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
                    elif keys[pygame.K_SPACE]:
                        self.logger.info("Land")
                        a.land()
                    elif keys[pygame.K_q]:
                        self.logger.info("Emergency")
                        a.emergency()
                        self.is_running = False
                        break

                if event.type == pygame.KEYUP:
                    keys = pygame.key.get_pressed()
            clock1.tick(64)

        a.disconnect()
        pygame.quit()


if __name__ == '__main__':
    unittest.main()
