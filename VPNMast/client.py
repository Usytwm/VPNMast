from Proto.udp import UDP
from core import Body

import config
import json
import sys

user = input("user: ")
password = input("password: ")
dest_ip = input("destination ip: ")
dest_port = int(input("destination port: "))
data = input("Introduce the data: ")

body = Body(dest_ip, dest_port, data)
body = json.dumps(body, default=lambda o: o.__dict__)

client =UDP(config.IP, 5001)

client.send(body,('localhost', config.PORT))
