import json
import logging
import os
import urllib
import webbrowser

import oauth2 as oauth

import requests
import time

import settings
from agent.agent import CloudDeviceAgent
from enum import Enum


logging.basicConfig(format="[%(name)s][%(asctime)s] %(message)s", level=logging.INFO)
logger = logging.getLogger("WithingsAgent")

MEASTYPE_NAME_UNIT = {
    1: ("weight", "kg"),
    4: ("height", "meter"),
    5: ("fat free mass", "kg"),
    6: ("fat ratio", "percent"),
    8: ("fat", "kg"),
    9: ("diastolic", "mmHg"),
    10: ("systolic", "mmHg"),
    11: ("pulse", "bpm"),
    54: ("spo2", "percent")
}


class MEASTYPE(Enum):
    weight = 1
    height = 4
    fat_free_mass = 5
    fat_ratio = 6
    fat = 8
    diastolic = 9
    systolic = 10
    pulse = 11
    spo2 = 54


class WithingsAgent(CloudDeviceAgent):

    REQUEST_TOKEN_URL = 'https://oauth.withings.com/account/request_token'
    AUTHORIZE_URL = 'https://oauth.withings.com/account/authorize'
    ACCESS_TOKEN_URL = 'https://oauth.withings.com/account/access_token'
    API_URL = 'http://wbsapi.withings.net/measure'
    EXPIRATION_TIME = 20 * 60 - 10  # 20 minues - 10 seconds
    instance = None
    CACHE_PATH = os.path.join(settings.BASE_DIR, "cache/withings")


    def __init__(self, fwk_user_id, device_item_id, key, secret, server_addr, server_port=5000):
        self.fwk_user_id = fwk_user_id
        self.device_item_id = device_item_id
        self.consumer_key = key
        self.consumer_secret = secret
        self.server_addr = server_addr
        self.is_connected = False
        self.is_authorized = False

        self.CALLBACK_URL = '%s:%s/cb/withings' % (server_addr, server_port)
        self.REQUEST_TOKEN_URL = "%s?oauth_callback=%s" % (self.REQUEST_TOKEN_URL, self.CALLBACK_URL)
        WithingsAgent.instance = self

    def connect(self):
        self.consumer = oauth.Consumer(self.consumer_key, self.consumer_secret)
        self.client = oauth.Client(self.consumer)

        if self.load_cache():
            self.access()
            self.is_connected = True
            return True

        if self.get_request_token():
            result = self.authorize()
            if not result:
                logger.info("Connection Failed. No internet connection.")
                return False
        else:
            logger.info("Connection Failed.")
            return False
        self.is_connected = True
        return True

    def disconnect(self):
        pass

    def get_request_token(self):
        """ Step 1. Request Token
        :return:
        """

        try:
            # Check internet connectivity
            _ = requests.get(self.REQUEST_TOKEN_URL, timeout=1)
            resp, content = self.client.request(self.REQUEST_TOKEN_URL, "GET")
        except requests.ConnectionError:
            return False

        content = content.decode("utf-8")
        logger.info("[Request Token] Response: %s" % resp)
        if resp['status'] != '200':
            raise Exception("[Request Token] Invalid response %s." % resp['status'])
        self.request_token = dict(urllib.parse.parse_qsl(content))  # return list of name/value pairs
        if "oauth_token" in self.request_token and "oauth_token_secret" in self.request_token:
            logger.info("[Request Token] Content:")
            logger.info("\t- oauth_token\t= %s" % self.request_token['oauth_token'])
            logger.info("\t- oauth_token_secret\t= %s" % self.request_token["oauth_token_secret"] if "oauth_token_secret" in self.request_token else "None")
        else:
            return False
        return True

    def authorize(self):
        """ Step 2. End-User Authorization
        :return:
        """
        # logger.info("[End-User Authorization] Go to the following link in your browser:")
        # logger.info("\t- %s?oauth_token=%s" % (self.authorize_url, self.d["conn"]["request_token"]['oauth_token']))
        logger.info("[End-User Authorization] A web site for authorization will be open.")

        try:
            # Check internet connectivity
            _ = requests.get("%s?oauth_token=%s" % (self.AUTHORIZE_URL, self.request_token['oauth_token']), timeout=1)
            # Open browser
            webbrowser.open("%s?oauth_token=%s" % (self.AUTHORIZE_URL, self.request_token['oauth_token']))
            return True
        except requests.ConnectionError:
            return False

            # accepted = 'n'
            # while accepted.lower() == 'n':
            #     accepted = raw_input('\t- Have you authorized me? (y/n) ')
            # self.d["conn"]["oauth_verifier"] = raw_input('\t- What is the PIN? ')

    def access(self):
        """ Step 3. Access Token
        :return:
        """
        token = oauth.Token(self.request_token['oauth_token'],
                            self.request_token['oauth_token_secret'])
        token.set_verifier(self.oauth_verifier)
        self.client = oauth.Client(self.consumer, token)

        try:
            # Check internet connectivity
            _ = requests.get(self.ACCESS_TOKEN_URL, timeout=1)
            resp, content = self.client.request(self.ACCESS_TOKEN_URL, "POST")
        except requests.ConnectionError:
            return False

        content = content.decode("utf-8")
        self.access_token = dict(urllib.parse.parse_qsl(content))
        logger.info("[Access Token] Content: %s" % self.access_token)

        if "oauth_token" in self.access_token and "oauth_token_secret" in self.access_token:
            token = oauth.Token(self.access_token['oauth_token'],
                                self.access_token['oauth_token_secret'])
            self.client = oauth.Client(self.consumer, token)
        else:
            self.connect()
            return False

        return True

    def acquire(self, meastype, limit=10):
        """http://wbsapi.withings.net/measure?
        action=getmeas&
        oauth_consumer_key=f853b4e9edc1fc75e367fbb60c1b5ff2833b16e2d34d3d5f99055bb560d&
        oauth_nonce=3ac21b822f84682a218493a918e444b0&
        oauth_signature=0xmUGyijFV348S1Qf9E32sc2ySE%3D&
        oauth_signature_method=HMAC-SHA1&
        oauth_timestamp=1430466875&d
        oauth_token=&
        oauth_version=1.0&
        userid="""

        try:
            # request_url = API_URL+\
            #               "?action=%s&" \
            #               "userid=%s&" \
            #               "startdate=%s&" \
            #               "meastype=%d&" \
            #               "limit=%d" % ('getmeas', self.d["conn"]["userid"], startdate+1, meastype, limit)
            request_url = self.API_URL+\
                          "?action=%s&" \
                          "userid=%s&" \
                          "meastype=%d&" \
                          "limit=%d"% ('getmeas', self.userid, meastype.value, limit)

            try:
                # Check internet connectivity
                _ = requests.get(request_url, timeout=1)
                # Acquire measurements
                resp, content = self.client.request(request_url, "GET")
            except requests.ConnectionError:
                return None
            content = content.decode("utf-8")
            content = json.loads(content)

            logger.info("[Acquire] Request URL: %s" % request_url)
            logger.info("[Acquire] Contexts:")
            logger.info("%s" % content)

            if content is not None and 'body' in content and len(content['body']['measuregrps']) > 0:
                measgrp = content['body']['measuregrps']
                for meas in measgrp:
                    for m in meas['measures']:
                        typeunit = MEASTYPE_NAME_UNIT[int(m['type'])]
                        data = {
                            "time": int(meas["date"])*1000,
                            "type": typeunit[0],
                            "unit": typeunit[1],
                            "value": m["value"]
                        }
                        self.transmit(data)
                    # {'attrib': 0, 'category': 1, 'measures': [{'unit': 0, 'value': 71, 'type': 11}], 'date': 1466495266, 'grpid': 563292070}, {'attrib': 0, 'category': 1, 'measures': [{'unit': 0, 'value': 68, 'type': 11}], 'date': 1466494436, 'grpid': 563287057}], 'updatetime': 1466496055}, 'status': 0}

            return content
        finally:
            pass

    def cache(self):
        with open(self.CACHE_PATH, 'w+') as f:
            f.write("%s\n" % str(int(time.time())))
            f.write("%s" %
                    json.dumps({"request_token": self.request_token,
                                "oauth_verifier": self.oauth_verifier,
                                "userid": self.userid,
                                "access_token": self.access_token}))
            f.close()

    def load_cache(self):
        if os.path.isfile(self.CACHE_PATH):
            with open(self.CACHE_PATH, "r") as f:
                cache_time = int(f.readline())

                if time.time()-cache_time > 20*60:  # more than 20 minutes
                    return False

                conf = f.readline()
                conf = json.loads(conf)
                self.request_token = conf["request_token"]
                self.userid = conf["userid"]
                self.access_token = conf["access_token"]
                self.oauth_verifier = conf["oauth_verifier"]
                self.is_authorized = True
                return True
        return False