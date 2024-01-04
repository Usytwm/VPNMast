import socket
import struct
from ipaddress import ip_address
import os
import json
from core import Address, Body
from utils import *


class UDP:
    def __init__(self, ip, port):
        self._ip = "127.0.0.1" if ip == "localhost" else ip
        self._port = port
        self.__stop = False
        self.conexiones: dict[str, Address] = {}
        self.__connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__connection.bind((self._ip, self._port))

    def send(self, data, dest_addr):
        """
        Envía datos a una dirección de destino a través de una conexión UDP.

        Args:
        data (str): Los datos a enviar.
        dest_addr (tuple): Una tupla que contiene la dirección IP de destino (str) y el puerto de destino (int).

        Returns:
        None
        """
        dest_ip, dest_port = dest_addr
        dest_ip = "127.0.0.1" if dest_ip == "localhost" else dest_ip

        data = data.encode("utf-8")

        udp_data = make_udp(self._port, dest_port, data)

        ip_data = make_ipv4(socket.IPPROTO_UDP, self._ip, dest_ip, udp_data)

        self.__connection.sendto(ip_data, (dest_ip, dest_port))

        print(f"UDP data sent to {dest_ip}:{dest_port}\n")

    def run(self):
        """
        Inicia el servidor y lo mantiene en funcionamiento hasta que se detiene.

        Args:
        Ninguno

        Returns:
        data o body (str): Los datos recibidos del cliente o el cuerpo del paquete, respectivamente.
        """
        while not self.__stop:
            try:
                data, src_addr = self.__connection.recvfrom(1024)
                proto, src_ip, dst_ip, ip_data = parse_ipv4(data)

                if proto != socket.IPPROTO_UDP:
                    continue

                src_port, dest_port, udp_data = parse_udp(ip_data)

                if dest_port != self._port:
                    continue

                sender_ip, _ = src_addr

                # Extrae el checksum del encabezado UDP
                received_checksum = struct.unpack(">H", ip_data[6:8])[0]

                # Crea un encabezado UDP con el checksum establecido en 0
                zero_checksum_header = ip_data[:6] + b"\x00\x00" + ip_data[8:]

                # Calcula el checksum
                calculated_checksum = checksum(zero_checksum_header)

                print(f"UDP data received from {sender_ip}:{src_port}")

                # Convertir la cadena de texto a un diccionario
                datos = json.loads(udp_data.decode("utf-8"))

                # Comprobar si 'dest_ip' y 'dest_port' existen en el diccionario
                if (
                    isinstance(datos, dict)
                    and datos.get("dest_ip") is not None
                    and datos.get("dest_port") is not None
                ):
                    if received_checksum != calculated_checksum:
                        print("Corrupted data\n")
                    else:
                        data = udp_data.decode("utf-8")
                        _address = Address(src_ip.compressed, src_port)
                        self.conexiones[
                            f"{datos.get('dest_ip')}:{datos.get('dest_port')}"
                        ] = [datos.get("user"), datos.get("password")], _address
                        print(f"Data: {data}\n")
                    yield data
                else:
                    dat, _address = self.conexiones[f"{sender_ip}:{src_port}"]
                    body = Body(
                        _address.ip,
                        _address.port,
                        json.dumps({"ip": sender_ip, "port": src_port, "data": datos}),
                        dat[0],
                        dat[1],
                    )
                    body = json.dumps(body, default=lambda o: o.__dict__)
                    print(f"Data: {body}\n")
                    yield body

            except BlockingIOError:
                continue

    def stop(self):
        """
        Este método detiene el servidor.

        Args:
        Ninguno

        Returns:
        Ninguno
        """
        self.__stop = True

    def socket(
        self,
    ) -> socket.socket:
        """
        Devuelve la conexión de socket actual.

        Returns:
            socket.socket: La conexión de socket actual.
        """
        return self.__connection

    def settimeout(self, timeout):
        """
        Establece un tiempo de espera para la conexión de socket.

        Args:
            timeout: El tiempo de espera en segundos.
        """
        self.__connection.settimeout(timeout)
