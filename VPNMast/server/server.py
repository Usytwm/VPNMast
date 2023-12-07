# server.py
import socket
#from  VPNMast.Networking.ip import parse_ipv4, parse_tcp

import struct
import threading

def parse_ipv4(packet):
    ip_header = packet[:20]  # Tamaño del encabezado IP
    iph = struct.unpack('!BBHHHBBH4s4s', ip_header)

    version_ihl = iph[0]
    version = version_ihl >> 4
    ihl = version_ihl & 0xF

    iph_length = ihl * 4

    ttl = iph[5]
    protocol = iph[6]
    s_addr = socket.inet_ntoa(iph[8])
    d_addr = socket.inet_ntoa(iph[9])

    return protocol, s_addr, d_addr, packet[iph_length:]

def parse_tcp(packet):
    tcp_header = packet[:20]  # Tamaño del encabezado TCP
    tcph = struct.unpack('!HHLLBBHHH', tcp_header)

    source_port = tcph[0]
    dest_port = tcph[1]
    sequence = tcph[2]
    acknowledgement = tcph[3]
    doff_reserved = tcph[4]
    tcph_length = doff_reserved >> 4

    return source_port, dest_port, tcph_length, packet[20:]


class VPNServer:
    def __init__(self):
        self.connections = {}

    def handle_client(self, client_socket, client_address):
        while True:
            # Recibir datos del cliente
            data = client_socket.recv(1024)
            if not data:
                break

            # Analizar el paquete IP
            proto, src_ip, dst_ip, ip_body = parse_ipv4(data)

            # Analizar el paquete TCP
            src_port, dst_port, flag, tcp_body = parse_tcp(ip_body)

            # Imprimir la dirección IP de origen y destino y el contenido del mensaje
            print(f"Datos recibido de {src_ip}:{src_port}, redirigido a {dst_ip}:{dst_port}")
            print(f"Datos: {tcp_body.decode()}")
            
            # !error a partir de aki

            # Crear un nuevo socket para la conexión redirigida
            redirect_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            redirect_socket.connect((dst_ip, dst_port))

            # # Enviar los datos al destino redirigido
            redirect_socket.send(tcp_body)

            # # Recibir la respuesta del destino redirigido
            response = redirect_socket.recv(1024)

            # # Enviar la respuesta al cliente
            client_socket.send(response)

            redirect_socket.close()
            #!hasta aki

        client_socket.close()

    def start(self, host, port):
        server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_socket.bind((host, port))
        server_socket.listen(1)

        print("Esperando conecciones")
        while True:
            # Aceptar una conexión entrante
            client_socket, client_address = server_socket.accept()
            print(f"Conexión aceptada de {client_address}")
            
            self.connections[client_address] = client_socket
            
            # Iniciar un nuevo hilo para manejar la conexión
            client_thread = threading.Thread(target=self.handle_client, args=(client_socket, client_address))
            client_thread.start()

server = VPNServer()
server.start('127.0.0.1', 12345)
