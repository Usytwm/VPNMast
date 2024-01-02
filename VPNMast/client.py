import socket
from udp import UDP
from utils import parse_ipv4, parse_udp, get_user
from core import Body
import config
import json

client = UDP(config.IP, 5001)
while True:

    user = input("user: ")
    password = input("password: ")
    if not get_user(user, password) == None:
        while True:
            dest_ip = input("destination ip: ")
            dest_port = int(input("destination port: "))
            data = input("Introduce the data: ")

            body = Body(dest_ip, dest_port, data)
            body = json.dumps(body, default=lambda o: o.__dict__)

            client.send(body, ("localhost", config.PORT))
            try:
                client.settimeout(1)
                data, server = client.socket().recvfrom(1024)
                proto, src_ip, dst_ip, ip_data = parse_ipv4(data)
                src_port, dest_port, udp_data = parse_udp(ip_data)
                decode = udp_data.decode("utf-8")
                decode = json.loads(decode)
                response_body = Body(decode["ip"], int(decode["port"]), decode["data"])
                print(
                    f"Recived from {response_body.dest_ip}:{response_body.dest_port} -> {response_body.data}"
                )
            except socket.timeout:
                # print("The server did not respond")
                continue
    else:
        print(
            "There is an error with your creadentials. Sign up or verificate your credentials or type exit"
        )
        ex = input()
        if ex == "exit":
            break
        else: continue
