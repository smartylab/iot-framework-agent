import json
import logging
import os
import socket
import sys
import time

import serial

from libs import sphero_driver, sumo
from libs.minidrone import minidrone
from connection import Connector

logger = logging.getLogger("IoT Device Agent")
logger.setLevel(logging.INFO)


SPHEROBALL = "SPHEROBALL"
ROLLINGSPIDER = "ROLLINGSPIDER"
EHEALTHSENSORKIT = "EHEALTHSENSORKIT"


class DeviceConnector(object):

    def connect(self):
        pass

    def disconnect(self):
        pass


class SerialDeviceConncector(DeviceConnector):

    def list_ports(self):
        import serial.tools.list_ports
        if os.name == 'nt':
            return list(serial.tools.list_ports.comports())


class BluetoothDeviceConnector(DeviceConnector):

    def discover(self):
        pass

    @staticmethod
    def discover_all():
        pass


class EHealthKitConnector(DeviceConnector):

    class Measurement:
        PULSE = "pulse"
        SPO2 = "spo2"
        BLOOD_PRESSURE = "blood pressure"
        GLUCOSE = "glucose"
        ECG = "ecg"
        EMG = "emg"
        GSR = "gsr"
        EEG = "eeg"
        TEMPERATURE = "temperature"
        WEIGHT = "weight"
        FAT = "fat"

    addr_list = [
        "COM18",
    ]

    def __init__(self, addr=None, user_id=1):
        self.serial_conn = None
        self.addr = addr if addr is not None else self.addr_list[0]
        self.connect()
        self.connector = Connector(user_id, device_addr=addr)

    def connect(self):
        super().connect()
        self.serial_conn = serial.Serial(self.addr, 115200, timeout=10)

    def disconnect(self):
        super().disconnect()
        if self.serial_conn is not None:
            self.serial_conn.close()

    def acquire_meas(self, meas_type, num=1, duration=0, interval=0.02, retry=1):
        """
        :param meas_types: a list of measurement types like ['pulse', 'ecg']
        :return: acquired measurements as a json array
        """

        context = None
        time_from = time.time()
        while True:
            # write to seiral for request measurement
            self.serial_conn.write(bytes(self._build_cmd(meas_type), 'UTF-8'))

            # read measurements
            serial_line = self.serial_conn.readline()
            if serial_line is None:
                time.sleep(retry)
                continue
            serial_line = serial_line.decode('UTF-8')
            values = serial_line.rstrip().split(',')

            # build a context
            context = self._build_context(meas_type, values)
            if context is None:
                time.sleep(retry)
                continue

            # check the elapsed time
            if time.time()-time_from >= duration:
                break

        return context

    def _build_cmd(self, meas_type):
        return 'MEAS:' + meas_type + '\n'

    def _build_context(self, meas_type, values):
        if meas_type == self.Measurement.PULSE:
            if len(values) != 2:
                logger.error("Invalid values for the measurement type, %s" % meas_type)
                return None

            pulse = float(values[0])
            spo2 = float(values[1])

            # if pulse <= 0. or spo2 <= 0.:
            #     logger.error("One or both of the values are zero: %s" % ([pulse, spo2]))
            #     return None
            # TODO: Uncomment

            return {
                'type': meas_type,
                'time': int(time.time()*1000), # TODO: Change to time
                'data': [
                    {'sub_type': 'pulse', 'value': pulse, 'unit': 'bpm'},
                    {'sub_type': 'pulse', 'value': spo2, 'unit': '%'},
                ]
            }

    def test(self):
        tr = Connector()

        while True:
            context = self.acquire_meas(self.Measurement.PULSE)

            print(context)
            tr.transmit(context)
            time.sleep(1)


class SpheroBallAgent(BluetoothDeviceConnector):

    addr_list = [
        "68:86:E7:04:A6:B4",
    ]
    sphero = sphero_driver.Sphero()

    def __init__(self, addr):
        self.tr = None
        self.conn = None
        self.connected = False
        self.addr = addr if addr is not None else self.addr_list[0]
        self.connect()

    def connect(self):
        self.conn = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.conn.connect((self.addr, 1))
        self.connected = True

    def disconnect(self):
        self.connected = False
        if self.conn is not None:
            self.conn.close()

    def roll(self, speed=50, heading=0, state=0x01):
        self.conn.send(self.sphero.msg_roll(speed, heading, state, False))

    def test(self):
        self.connect()
        print("Connected.")
        while not self.connected:
            time.sleep(1)
        for _ in range(10):
            self.roll()
            time.sleep(1)
        self.disconnect()
        print("Disconnected.")


class RollingSpiderController(BluetoothDeviceConnector):

    addr_list = [
        "E0:14:9F:34:3D:4F",
    ]

    def __init__(self, addr=None):
        self.drone = None
        self.connected = False
        self.addr = addr if addr is not None else self.addr_list[0]
        self.connect()

    def connect(self):
        self.drone = minidrone.MiniDrone(mac=self.addr, callback=self.callback)
        self.drone.connect()
        self.connected = True

    def disconnect(self):
        self.connected = False
        if self.drone is not None:
            self.drone.disconnect()

    def ascend(self):
        self.drone.ascend()

    def descend(self):
        self.drone.descend()

    def turn_left(self):
        self.drone.turn_left()

    def turn_right(self):
        self.drone.turn_right()

    def move_fw(self):
        self.drone.move_fw()

    def move_bw(self):
        self.drone.move_bw()

    def move_right(self):
        self.drone.move_right()

    def move_left(self):
        self.drone.move_left()

    def still(self):
        self.drone.still()

    def incr_speed(self):
        self.drone.incr_speed()

    def decr_speed(self):
        self.drone.decr_speed()

    def takeoff(self):
        self.drone.takeoff()

    def land(self):
        self.drone.land()

    def emergency(self):
        self.drone.emergency()

    def get_speed(self):
        return self.drone.speed

    @staticmethod
    def callback(t, data):
        pass

    def test(self):
        self.connect()
        print("Connected.")
        time.sleep(1)
        self.takeoff()
        time.sleep(3)
        self.land()
        time.sleep(1)
        self.disconnect()
        print("Disconnected.")


class JumpingSumoController(BluetoothDeviceConnector):

    addr_list = [
        "E0:14:9F:34:3D:4F",
    ]

    def __init__(self):
        self.drone = None
        self.connected = False
        self.connect()

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


if __name__ == '__main__':
    # SpheroController().test()
    # RollingSpiderController().test()
    EHealthKitConnector().test()
    # print(SerialDeviceConncector().list_ports())
    sys.exit(1)
