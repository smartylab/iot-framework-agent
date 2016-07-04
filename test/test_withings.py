import json
import logging
import threading
import unittest

import time

import requests

import settings
import withings_callback
from agent.withings_agent import WithingsAgent, MEASTYPE

logging.basicConfig(format="[%(name)s][%(asctime)s] %(message)s", level=logging.INFO)


if __name__ == '__main__':
    unittest.main()
