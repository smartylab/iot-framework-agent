import json
import logging
import sys

import requests

import agent
import settings

logger = logging.getLogger("IoT Device Agent")
logger.setLevel(logging.INFO)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        logger.error("Wrong usage. Need to enter a command.\nUsage: python manage.py <command> [<param>, ...]")
        sys.exit(0)

    command = sys.argv[1]

    if command == "connect":
        if len(sys.argv) < 3:
            logger.error("Wrong usage.\nUsage: python manage.py %s <device_item_id> -u <user_id> -p <password>" % command)
            sys.exit(0)

        device_item_id = sys.argv[2]
        user_id = None
        password = None

        if len(sys.argv) > 3:
            if (len(sys.argv)-3)%2 > 0:
                logger.error("Wrong usage. Please check the entered options.")
                sys.exit(0)
            for opt, val in zip(sys.argv[3::2], sys.argv[4::2]):
                if opt == '-u':
                    user_id = val
                elif opt == '-p':
                    password = val
        try:
            data = {
                "device_item_id": device_item_id
            }
            if user_id is not None:
                data['user_id'] = user_id
            if password is not None:
                data['password'] = password

            logger.info("Try to connect with %s" % data)
            r = requests.post(settings.CONTEXT_API, data=json.dumps(data))
            r = r.json()

            # TODO: Initialize a device agent
        except Exception as e:
            logger.error(e)

