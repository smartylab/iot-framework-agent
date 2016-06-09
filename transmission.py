import json

import requests


class Transmitter(object):

    def __init__(self, addr):
        self.addr = addr

    def handshake(self):
        pass

    def transmit(self, data):
        requests.post(self.addr, data=json.dumps(data))

