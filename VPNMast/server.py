from Proto.udp import UDP
import sys

port = int(input("port: "))
server = UDP('localhost', port)

print(f'Server UDP started in port: {port} \n')
for i in server.run():
    print(f'Received: {i}\n')
    print('================================\n')