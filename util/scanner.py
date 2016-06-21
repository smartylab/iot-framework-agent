import socket

from agent.libs import sphero_driver
sphero = sphero_driver.Sphero()

mac = "68:86:E7:04:A6:B4"   # Sphero
# mac = "e0:14:9f:34:3d:4f"   # RS
port = 1

s = socket.socket(socket.AF_BLUETOOTH, socket.SOCK_STREAM, socket.BTPROTO_RFCOMM)

s.connect((mac, port))
s.send(sphero.msg_roll(70, 0, 0x01, False))

s.close()