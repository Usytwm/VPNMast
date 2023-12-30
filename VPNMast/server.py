import socket
import struct
from udp import UDP
from utils import parse_ipv4, parse_udp, make_ipv4, make_udp, checksum

port = int(input("port: "))
_ip = "127.0.0.1"
_port = port
__connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
__connection.bind((_ip, _port))

print(f"Server UDP started in port: {port} \n")

while True:
    try:
        data, src_addr = __connection.recvfrom(1024)
        proto, src_ip, dst_ip, ip_data = parse_ipv4(data)

        if proto != socket.IPPROTO_UDP:
            continue

        src_port, dest_port, udp_data = parse_udp(ip_data)

        if dest_port != _port:
            continue

        sender_ip, _ = src_addr

        # Extrae el checksum del encabezado UDP
        received_checksum = struct.unpack(">H", ip_data[6:8])[0]

        # Crea un encabezado UDP con el checksum establecido en 0
        zero_checksum_header = ip_data[:6] + b"\x00\x00" + ip_data[8:]

        # Calcula el checksum
        calculated_checksum = checksum(zero_checksum_header)

        print(f"UDP data received from {sender_ip}:{src_port}")

        if received_checksum != calculated_checksum:
            print("Corrupted data\n")
        else:
            data = udp_data.decode("utf-8")
            print(f"Data: {data}\n")

    except BlockingIOError:
        continue
