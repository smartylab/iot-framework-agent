import logging
import sys

import device

logger = logging.getLogger("IoT Device Agent")
logger.setLevel(logging.INFO)


if __name__ == '__main__':

    if len(sys.argv) != 3:
        logger.error("Wrong usage. \nUsage: python manage.py <device_name> <device_addr>")
        sys.exit(0)

    device_name = sys.argv[1].upper()
    device_addr = sys.argv[2]

    if device_name == device.SPHEROBALL:
        print(device_name)
    elif device_name == device.ROLLINGSPIDER:
        pass
    elif device_name == device.EHEALTHSENSORKIT:
        pass
