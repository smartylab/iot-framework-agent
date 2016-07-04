import json
import logging
import sys
import unittest

import requests

import settings

logger = logging.getLogger("IoT Device Agent")
logger.setLevel(logging.INFO)


if __name__ == '__main__':

    if len(sys.argv) < 2:
        logger.error("Wrong usage. Need to enter a command.\nUsage: python manage.py <command> [params]")
        sys.exit(0)

    command = sys.argv[1]

    if command == "test":
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
            connection_data = {
                "device_item_id": int(device_item_id)
            }
            if user_id is not None:
                connection_data['user_id'] = user_id
            if password is not None:
                connection_data['password'] = password

            logger.info("Try to connect with %s" % connection_data)
            res = requests.post(settings.CONNECT_API, data=json.dumps(connection_data))
            device = res.json()

            logger.info(device)
            """
            {'device_item': {'item_name': 'Rolling Spider 1', 'item_id': 7, 'connected': False, 'model_id': 18,
                             'item_address': 'E0:14:9F:34:3D:4F', 'user_id': 'mkkim'},
             'device_model': {'model_name': 'Rolling Spider', 'model_id': 18, 'model_network_protocol': 'Bluetooth'},
             'user_id': 'mkkim', 'code': 'SUCCESS'}
             """
            if device['code'] == 'SUCCESS':
                device_model_name = device['device_model']['model_name']
                device_item_addr = device['device_item']['item_address']

                tester = unittest.TextTestRunner(verbosity=2)
                if device_model_name == 'Rolling Spider':
                    pass
                elif device_model_name == 'Sphero Ball 2':
                    pass
                elif device_model_name == 'e-Health Sensor Kit':
                    from test.test_ehealthkit import EHealthKitAgentTestCase
                    tester.run(EHealthKitAgentTestCase(device_item_addr))
                elif device_model_name == 'Withings':
                    pass
                else:
                    raise Exception("Not supported device model.")

                res = requests.delete(settings.CONNECT_API, data=json.dumps(connection_data)).json()
                logger.info(res)

            else:
                raise Exception("Fail to connect.")

        except Exception as e:
            logger.error(e)

