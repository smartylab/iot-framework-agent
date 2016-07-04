import json
import logging
import os
import socket
import time
import urllib
import webbrowser

import requests
import serial

import netifaces as ni
import oauth2 as oauth

import settings
from libs import sphero_driver, sumo
from libs.minidrone import minidrone

logger = logging.getLogger("IoT Device Agent")
logger.setLevel(logging.INFO)


SPHEROBALL = "SPHEROBALL"
ROLLINGSPIDER = "ROLLINGSPIDER"
EHEALTHSENSORKIT = "EHEALTHSENSORKIT"


class DeviceAgent(object):

    def connect(self):
        pass

    def disconnect(self):
        pass

    def transmit(self, data, is_series=False):
        if self.device_item_id is None:
            logger.error("Connection is not established.")
            return
        try:
            logger.debug("Transmitting context...")
            if not is_series:
                requests.post(settings.CONTEXT_API, data=json.dumps({
                    'device_item_id': self.device_item_id,
                    'context': data
                }))
            else:
                requests.post(settings.SERIES_CONTEXT_API, data=json.dumps({
                    'device_item_id': self.device_item_id,
                    'series_context': data
                }))
            logger.debug("Transmission done.")
        except Exception as e:
            logger.error("Transmission error.")


class SerialDeviceAgent(DeviceAgent):

    def list_ports(self):
        import serial.tools.list_ports
        if os.name == 'nt':
            return list(serial.tools.list_ports.comports())


class BluetoothDeviceAgent(DeviceAgent):

    def discover(self):
        pass

    @staticmethod
    def discover_all():
        pass


class CloudDeviceAgent(DeviceAgent):
    pass


class EHealthKitAgent(DeviceAgent):

    class Measurement:
        TEMPERATURE = "temperature"
        PULSESPO2 = "pulsespo2"
        ECG = "ecg"
        EMG = "emg"
        GSR = "gsr"
        EEG = "eeg"
        BLOOD_PRESSURE = "blood pressure"
        GLUCOSE = "glucose"

    subtypes = {
        Measurement.PULSESPO2: ['pulse', 'spo2'],
        Measurement.GSR: ['conductance', 'resistance', 'conductanceVol'],
        Measurement.BLOOD_PRESSURE: ['systolic', 'diastolic']
    }

    units = {
        Measurement.TEMPERATURE: 'degree Celsius',
        Measurement.GSR: ['bpm', 'percentage'],
        Measurement.PULSESPO2: ['micro second', 'ohm', 'voltage'],
        Measurement.ECG: 'voltage',
        Measurement.EMG: 'voltage',
        Measurement.BLOOD_PRESSURE: ['mmHg', 'mmHg'],
        Measurement.GLUCOSE: 'mg/dL',
    }

    addr_list = [
        "COM18",
    ]

    def __init__(self, user_id, device_item_id, addr):
        self.serial_conn = None
        self.user_id = user_id
        self.device_item_id = device_item_id
        self.addr = addr if addr is not None else self.addr_list[0]
        self.connect()

    def connect(self):
        super().connect()
        for _ in range(10):
            logger.info('Try to connect...')
            self.serial_conn = serial.Serial(self.addr, 115200, timeout=0.1)
            if self.serial_conn is not None:
                break

    def disconnect(self):
        super().disconnect()
        if self.serial_conn is not None:
            self.serial_conn.close()

    def acquire_context(self, meas_type, is_series=False, duration=10, interval=0.02, retry=1):
        """
        :param meas_types: a list of measurement types like ['pulse', 'ecg']
        :return: acquired measurements as a json array
        """

        context = None
        series_list = []
        time_from = time.time()
        while True:
            # write to seiral for request measurement
            self.serial_conn.write(bytes(self._build_cmd(meas_type), 'UTF-8'))

            # read measurements
            serial_line = self.serial_conn.readline()
            if serial_line is None or serial_line == b'':
                logger.debug('Retry writing...')
                time.sleep(retry)
                continue
            serial_line = serial_line.decode('UTF-8')
            values = serial_line.rstrip().split(',')
            logger.debug(values)

            if is_series:
                # accumulate series
                if len(series_list) == 0:
                    series_list = [[v] for v in values]
                else:
                    for s, v in zip(series_list, values):
                        s.append(v)
                # check the elapsed time
                time_to = time.time()
                if time_to-time_from >= duration:
                    context = self._build_context(meas_type, series_list, int(time_from*1000), time_to=int(time_to*1000))
                    break
                time.sleep(interval)
            else:
                # build a context
                context = self._build_context(meas_type, values, int(time_from*1000))
                if context is None:
                    time.sleep(retry)
                    continue
                break

        return context

    def _build_cmd(self, meas_type):
        return 'MEAS:' + meas_type + '\n'

    def _build_context(self, meas_type, values, time_from, time_to=None):
        if len(values) == 0:
            logger.error("Invalid values for the measurement type, %s" % meas_type)
            return None

        if meas_type in self.subtypes:
            context = {
                'type': meas_type,
                'data': [
                    {'sub_type': subtype, 'value': value, 'unit': unit}  for subtype, value, unit in zip(self.subtypes[meas_type], values, self.units[meas_type])
                ]
            }
        else:
            context = {
                'type': meas_type,
                'data': {'value': values[0], 'unit': self.units[meas_type]}
            }

        if time_to is None:
            context['time'] = time_from
        else:
            context['time_from'] = time_from
            context['time_to'] = time_to

        return context


class SpheroBallAgent(BluetoothDeviceAgent):

    sphero = sphero_driver.Sphero()

    def __init__(self, user_id, device_item_id, addr):
        self.tr = None
        self.conn = None
        self.connected = False
        self.user_id = user_id
        self.device_item_id = device_item_id
        self.addr = addr
        self.connect()
        self.speed = 0
        self.angle = 0

    def connect(self):
        self.conn = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)
        self.conn.connect((self.addr, 1))
        self.connected = True

    def disconnect(self):
        self.connected = False
        if self.conn is not None:
            self.conn.close()

    def roll(self, speed=50, heading=0, state=0x01):
        self.speed = speed*2/255
        self.angle = heading
        if self.connected:
            self.conn.send(self.sphero.msg_roll(speed, heading, state, False))

    def acquire_context(self):
        return {
            "type": "SpheroBall status",
            "time": int(time.time()*1000),
            "data": [
                {"sub_type": "speed", "value": self.speed, "unit": "m/s"},
                {"sub_type": "angle", "value": self.angle, "unit": "degree"}
            ]
        }


class RollingSpiderAgent(BluetoothDeviceAgent):

    agentstatuslist = ["Connecting", "Connected", "Disconnecting", "Disconnected", "Failed"]
    statuslist = ["Disconnected", "Init", "Connected", "Error"]

    def __init__(self, user_id, device_item_id, addr):
        self.status = self.agentstatuslist[3]
        self.drone = None
        self.connected = False
        self.user_id = user_id
        self.device_item_id = device_item_id
        self.addr = addr
        self.connect()

    def connect(self):
        self.status = self.agentstatuslist[0]
        self.drone = minidrone.MiniDrone(mac=self.addr, callback=self.callback)
        self.drone.connect()
        while self.status == self.agentstatuslist[0]:
                time.sleep(1)
        self.connected = self.status == self.agentstatuslist[1]

    def disconnect(self):
        self.connected = False
        if self.drone is not None:
            self.drone.disconnect()

    def ascend(self):
        if self.drone is not None:
            self.drone.ascend()

    def descend(self):
        if self.drone is not None:
            self.drone.descend()

    def turn_left(self):
        if self.drone is not None:
            self.drone.turn_left()

    def turn_right(self):
        if self.drone is not None:
            self.drone.turn_right()

    def move_fw(self):
        if self.drone is not None:
            self.drone.move_fw()

    def move_bw(self):
        if self.drone is not None:
            self.drone.move_bw()

    def move_right(self):
        if self.drone is not None:
            self.drone.move_right()

    def move_left(self):
        if self.drone is not None:
            self.drone.move_left()

    def still(self):
        if self.drone is not None:
            self.drone.still()

    def incr_speed(self):
        if self.drone is not None:
            self.drone.incr_speed()

    def decr_speed(self):
        if self.drone is not None:
            self.drone.decr_speed()

    def takeoff(self):
        if self.drone is not None:
            self.drone.takeoff()

    def land(self):
        if self.drone is not None:
            self.drone.land()

    def emergency(self):
        if self.drone is not None:
            self.drone.emergency()

    def get_speed(self):
        if self.drone is not None:
            return self.drone.speed

    def callback(self, t, data):
        logger.info("[%s] %s" % (t, data))
        if self.status == self.agentstatuslist[0]:  # Connecting
            if t == 4 and data == 'n':
                self.status = self.agentstatuslist[4]
                return
            elif t == 4 and data == 'y':
                self.status = self.agentstatuslist[1]
                return

        elif self.status == self.agentstatuslist[2]:  # Disconnecting
            if t == 4 and data == 'n':
                self.status = self.agentstatuslist[4]
                return
            elif t == 4 and data == 'y':
                self.status = self.agentstatuslist[3]
                return


    def acquire_context(self):
        return {
            "type": "RollingSpider status",
            "time": int(time.time()*1000),
            "data": [
                {"sub_type": "configured speed", "value": self.drone.speed, "unit": "cm/s"},
                {"sub_type": "status", "value": self.statuslist[self.drone.status]}
            ]
        }


class JumpingSumoAgent(BluetoothDeviceAgent):

    addr_list = [
        "E0:14:9F:34:3D:4F",
    ]

    def __init__(self):
        """Not supported"""
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