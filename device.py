import time
import sys

from libs import sphero_driver
from libs.minidrone import minidrone
from libs import sumo
import socket


class DeviceConnector(object):
    pass


class BluetoothDeviceConnector(DeviceConnector):

    def __init__(self):
        pass

    def discover_devices(self):
        pass

    def connect(self, addr):
        pass

    def disconnect(self):
        pass


class SpheroController(BluetoothDeviceConnector):

    mac_list = [
        "68:86:E7:04:A6:B4",
    ]
    sphero = sphero_driver.Sphero()

    def __init__(self):
        self.tr = None
        self.conn = None
        self.connected = False

    def connect(self, addr):
        self.conn = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.conn.connect((addr, 1))
        self.connected = True

    def disconnect(self):
        self.connected = False
        if self.conn is not None:
            self.conn.close()

    def roll(self, speed=50, heading=0, state=0x01):
        self.conn.send(self.sphero.msg_roll(speed, heading, state, False))

    def test(self):
        self.connect(self.mac_list[0])
        print("Connected.")
        while not self.connected:
            time.sleep(1)
        for _ in range(10):
            self.roll()
            time.sleep(1)
        self.disconnect()
        print("Disconnected.")


class RollingSpiderController(BluetoothDeviceConnector):

    mac_list = [
        "E0:14:9F:34:3D:4F",
    ]

    def __init__(self):
        self.drone = None
        self.connected = False

    def connect(self, addr):
        self.drone = minidrone.MiniDrone(mac=addr, callback=self.callback)
        self.drone.connect()
        self.connected = True

    def disconnect(self):
        self.connected = False
        if self.drone is not None:
            self.drone.disconnect()

    def takeoff(self):
        self.drone.takeoff()

    def land(self):
        self.drone.land()

    @staticmethod
    def callback(t, data):
        pass

    def test(self):
        self.connect(self.mac_list[0])
        print("Connected.")
        time.sleep(1)
        self.takeoff()
        time.sleep(3)
        self.land()
        time.sleep(1)
        self.disconnect()
        print("Disconnected.")


class JumpingSumoController(BluetoothDeviceConnector):

    mac_list = [
        "E0:14:9F:34:3D:4F",
    ]

    def __init__(self):
        self.drone = None
        self.connected = False

    def connect(self, addr):
        self.drone = sumo.SumoController('Sumo', host='')
        self.drone.connect()
        self.connected = True

    def disconnect(self):
        self.connected = False
        if self.drone is not None:
            self.drone.disconnect()

    def takeoff(self):
        self.drone.takeoff()

    def land(self):
        self.drone.land()

    @staticmethod
    def callback(t, data):
        pass

    def test(self):
        pass



def discover():
    BluetoothDeviceConnector().discover_devices()


if __name__ == '__main__':
    # SpheroController().test()
    # RollingSpiderController().test()
    sys.exit(1)
