from Proto.udp import UDP
import sys

server = UDP('localhost', 5002)

print('Server UDP started\n')
for i in server.run():
    print(f'Received: {i}\n')