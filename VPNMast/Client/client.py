from ..Proto.udp import UDP

import config
import json
import sys

user = input("user: ")
password = input("password: ")
dest_ip = input("destination ip: ")
dest_port = int(input("destination port: "))
data = input("Introduce the data: ")

client =UDP(config.IP, config.PORT)

client.send(data,('localhost', 5001))

# body = VPNBody(user, password, dest_ip, dest_port, data)
# body = json.dumps(body, default=lambda o: o.__dict__)

# args = sys.argv[1:]

# if len(args) == 0:
#     print("Invalid protocol")
#     exit()

# if args[0] == 'tcp':
#     client.send(body, ('localhost', 5001))
# elif args[0] == 'udp':
#     client.send(body, ('localhost', 5001))
# else:
#     print("Invalid protocol")