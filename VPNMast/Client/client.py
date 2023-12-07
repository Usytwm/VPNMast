# client.py
import socket
#from ..Networking.ip import make_ipv4,make_tcp

import socket
import struct

def make_ipv4(protocol, source_ip, dest_ip, body):
    # Construir el encabezado IP
    ip_version = 4
    ip_ihl = 5
    ip_ttl = 255
    ip_tot_len = 20 + len(body)  # Tamaño del encabezado IP + Tamaño del cuerpo
    ip_header = struct.pack('!BBHHHBBH4s4s', (ip_version << 4) + ip_ihl, 0, ip_tot_len, 0, 0, ip_ttl, protocol, 0, socket.inet_aton(source_ip), socket.inet_aton(dest_ip))

    return ip_header + body

def make_tcp(source_port, dest_port, data):
    # Construir el encabezado TCP
    tcp_seq = 1000
    tcp_ack_seq = 0
    tcp_offset_res = (5 << 4)
    tcp_flags = 2  # Flags SYN
    tcp_window = socket.htons(5840)
    tcp_check = 0
    tcp_urg_ptr = 0

    tcp_header = struct.pack('!HHLLBBHHH', source_port, dest_port, tcp_seq, tcp_ack_seq, tcp_offset_res, tcp_flags, tcp_window, tcp_check, tcp_urg_ptr)

    return tcp_header + data

class VPNClient:
    def __init__(self, server_host, server_port):
        self.server_host = server_host
        self.server_port = server_port

    def start(self):
        # Crear un socket
        client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        # Conectarse al servidor
        client_socket.connect((self.server_host, self.server_port))
        
        _, source_port = client_socket.getsockname()
        while True:
            # Solicitar al usuario la dirección IP y el puerto a los que desea enviar el mensaje
            dest_ip = input("IP: ")
            dest_port = int(input("puerto: "))

            # Enviar datos al servidor
            data = input("Datos: ")

            # Crear un paquete TCP/IP
            packet = make_ipv4(socket.IPPROTO_TCP, '127.0.0.1', dest_ip, make_tcp(source_port, dest_port, data.encode()))

            client_socket.send(packet)

            # # Recibir datos del servidor
            data = client_socket.recv(1024)
            print(f"Mensaje recibido del servidor: {data.decode()}")

        client_socket.close()


# class VPNClient:
#     def __init__(self, server_host, server_port):
#         self.server_host = server_host
#         self.server_port = server_port

#     def start(self):
#         # Crear un socket
#         client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

#         # Conectarse al servidor
#         client_socket.connect((self.server_host, self.server_port))

#         while True:
#             # Enviar datos al servidor
#             data = input("Introduce un mensaje para enviar al servidor: ")

#             # Crear un paquete TCP/IP
#             packet = make_ipv4(socket.IPPROTO_TCP, '127.0.0.1', self.server_host, make_tcp(12345, self.server_port, data.encode()))

#             client_socket.send(packet)

#             # Recibir datos del servidor
#             #data = client_socket.recv(1024)
#             #print(f"Mensaje recibido del servidor: {data.decode()}")

#         client_socket.close()

client = VPNClient('127.0.0.1', 12345)
client.start()
