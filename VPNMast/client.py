from Proto.udp import UDP
from core import Body

import config
import json
import sys

client =UDP(config.IP, 5001)
user = input("user: ")
password = input("password: ")

while True:
    dest_ip = input("destination ip: ")
    dest_port = int(input("destination port: "))
    data = input("Introduce the data: ")
   
    body = Body(dest_ip, dest_port, data)
    body = json.dumps(body, default=lambda o: o.__dict__)
    
    client.send(body,('localhost', config.PORT))
    
