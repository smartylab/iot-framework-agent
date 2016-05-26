import time
import sys
from libs import sphero_driver
import bluetooth
from pprint import pprint
import threading


registered_bluetooth_devices = [
    "68:86:E7:04:A6:B4",
]


class DeviceConnector(object):
    pass


class BluetoothDeviceConnector(DeviceConnector):

    def __init__(self):
        pass

    def discover_devices(self, devices=None):
        nearby_devices = bluetooth.discover_devices(lookup_names=True)
        # nearby_devices = bluetooth.discover_devices(duration=8, lookup_names=True, flush_cache=True, lookup_class=False)
        # print("found %d devices" % len(nearby_devices))
        for addr, name in nearby_devices:
            if not devices or (addr in devices):
                print("  %s - %s" % (addr, name))
                # pprint(bluetooth.find_service(address=addr))

    def connect(self, addr, name):
        pass


class SpheroController(BluetoothDeviceConnector):

    def __init__(self):
        self.tr = None
        self.sphero = None
        self.connected = False

    def connect(self, name=None, addr=None):
        def process(name, addr):
            self.sphero = sphero_driver.Sphero(target_name=name, target_addr=addr)
            try:
                if self.sphero.connect():
                    self.sphero.set_raw_data_strm(40, 1, 0, False)
                    self.sphero.start()
                    self.connected = True
            except Exception as e:
                print("Connection failed.")
        self.tr = threading.Thread(target=process, args=(name, addr))
        self.tr.start()

    def disconnect(self):
        if self.sphero:
            self.sphero.join()
            self.sphero.disconnect()
        if self.tr:
            self.tr.join()

    def roll(self, speed=20, heading=0, state=0x01):
        self.sphero.roll(speed, heading, state, False)



def test_sphero():
    sphero = SpheroController()
    sphero.connect(addr=registered_bluetooth_devices[0])
    while not sphero.connected:
        time.sleep(1)
    for _ in range(10):
        sphero.roll()
        time.sleep(1)
    sphero.disconnect()
    print("Disconnected.")


def discover():
    BluetoothDeviceConnector().discover_devices()


if __name__ == '__main__':
    discover()
    # test_sphero()
    sys.exit(1)
