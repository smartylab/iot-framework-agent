import json

import requests


class Transmitter(object):

    def __init__(self, addr):
        self.addr = addr

    def transmit(self, data):
        requests.post(self.addr, data=json.dumps(data))

