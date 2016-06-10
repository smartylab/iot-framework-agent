import logging
import sys

import device

logger = logging.getLogger("IoT Device Agent")
logger.setLevel(logging.INFO)


if __name__ == '__main__':

    if len(sys.argv) != 3:
        logger.error("Wrong usage. \nUsage: python manage.py <user_id> <device_name> <device_addr>")
        sys.exit(0)

    user_id = sys.argv[1]
    device_name = sys.argv[2].upper()
    device_addr = sys.argv[3]

    if device_name == device.SPHEROBALL:
        print(device_name)
    elif device_name == device.ROLLINGSPIDER:
        pass
    elif device_name == device.EHEALTHSENSORKIT:
        pass
