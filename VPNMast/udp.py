import socket
import struct
from ipaddress import ip_address
import os
import json
from core import Address, Body


class UDP:
    def __init__(self, ip, port):
        self._ip = "127.0.0.1" if ip == "localhost" else ip
        self._port = port
        self.__stop = False
        self.conexiones: dict[str, Address] = {}
        self.__connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__connection.bind((self._ip, self._port))

    def parse_udp(self, data):
        """
        Desempaqueta los datos UDP recibidos y extrae los puertos de origen y destino.

        Los primeros 4 bytes de los datos se desempaquetan como dos enteros sin signo de 16 bits en orden de bytes big-endian,
        que representan el puerto de origen y el puerto de destino, respectivamente.

        Luego, el método devuelve una tupla que contiene el puerto de origen, el puerto de destino y el resto de los datos.

        Args:
        data (bytes): Los datos UDP recibidos.

        Returns:
        src_port (int): El puerto de origen extraído de los datos.
        dst_port (int): El puerto de destino extraído de los datos.
        data[8:] (bytes): El resto de los datos después de los primeros 8 bytes.
        """
        src_port, dst_port = struct.unpack(">HH", data[:4])
        return src_port, dst_port, data[8:]

    def parse_ipv4(self, data):
        """
        Desempaqueta los datos IPv4 recibidos y extrae información relevante.

        Primero, extrae el campo IHL (Internet Header Length) de los datos, que indica la longitud del encabezado IPv4.
        Luego, extrae la longitud total del paquete, el protocolo utilizado, y las direcciones IP de origen y destino.

        Finalmente, extrae el cuerpo del paquete, que comienza después del encabezado IPv4 y termina en la longitud total del paquete.

        Args:
        data (bytes): Los datos IPv4 recibidos.

        Returns:
        proto (int): El protocolo utilizado.
        src_ip (IPv4Address): La dirección IP de origen.
        dst_ip (IPv4Address): La dirección IP de destino.
        body (bytes): El cuerpo del paquete.
        """
        ihl = data[0] & 0x0F
        length = int.from_bytes(data[2:4], "big")
        proto = data[9]
        src_ip = ip_address(data[12:16])
        dst_ip = ip_address(data[16:20])
        body = data[ihl << 2 : length]
        return proto, src_ip, dst_ip, body

    def make_udp(self, src_port, dst_port, body):
        """
        Crea un paquete UDP. Se calcula el checksum del paquete UDP completo.
        Crea el encabezado UDP con el checksum calculado y se une con el cuerpo
        del paquete.

        Args:
        src_port (int): El puerto de origen.
        dst_port (int): El puerto de destino.
        body (bytes): El cuerpo del paquete.

        Returns:
        bytes: El paquete UDP completo, incluyendo el encabezado y el cuerpo.
        """
        udp_data = struct.pack(">HHHH", src_port, dst_port, len(body) + 8, 0) + body
        checksum = self.checksum(udp_data)
        return struct.pack(">HHHH", src_port, dst_port, len(body) + 8, checksum) + body

    def make_ipv4(self, proto, src_ip, dst_ip, body):
        """
        Crea un paquete IPv4.

        Este método construye un encabezado IPv4 con un checksum inicial de 0 y lo concatena con el cuerpo del paquete.
        Luego, calcula el checksum del paquete IPv4 completo. Finalmente, inserta el checksum calculado en el encabezado IPv4
        y devuelve el paquete IPv4 completo.

        Args:
        proto (int): El protocolo a utilizar.
        src_ip (str): La dirección IP de origen.
        dst_ip (str): La dirección IP de destino.
        body (bytes): El cuerpo del paquete.

        Returns:
        bytes: El paquete IPv4 completo, incluyendo el encabezado y el cuerpo.
        """
        ip_header = bytearray(
            struct.pack(
                ">BxH2s2xBB2x4s4s",
                0x45,
                len(body) + 20,
                os.urandom(2),
                64,
                proto,
                ip_address(src_ip).packed,
                ip_address(dst_ip).packed,
            )
        )
        checksum = self.checksum(ip_header + body)
        ip_header[10:12] = checksum.to_bytes(
            2, "big"
        )  # Convierte el checksum en una secuencia de bytes
        return bytes(ip_header + body)

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

        udp_data = self.make_udp(self._port, dest_port, data)

        ip_data = self.make_ipv4(socket.IPPROTO_UDP, self._ip, dest_ip, udp_data)

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
                proto, src_ip, dst_ip, ip_data = self.parse_ipv4(data)

                if proto != socket.IPPROTO_UDP:
                    continue

                src_port, dest_port, udp_data = self.parse_udp(ip_data)

                if dest_port != self._port:
                    continue

                sender_ip, _ = src_addr

                # Extrae el checksum del encabezado UDP
                received_checksum = struct.unpack(">H", ip_data[6:8])[0]

                # Crea un encabezado UDP con el checksum establecido en 0
                zero_checksum_header = ip_data[:6] + b"\x00\x00" + ip_data[8:]

                # Calcula el checksum
                calculated_checksum = self.checksum(zero_checksum_header)

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
                        ] = _address
                        print(f"Data: {data}\n")
                    yield data
                else:
                    _address = self.conexiones[f"{sender_ip}:{src_port}"]
                    body = Body(
                        _address.ip,
                        _address.port,
                        json.dumps({"ip": sender_ip, "port": src_port, "data": datos}),
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

    @staticmethod
    def checksum(data):
        """
        Este método calcula y devuelve el checksum de los datos proporcionados.

        Args:
            data: Los datos para los que se calculará el checksum.

        Returns:
            int: El checksum de los datos, representado como un entero de 16 bits.
        """
        checksum = 0
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                checksum += (data[i] << 8) + data[i + 1]
            else:
                checksum += data[i]
            while checksum >> 16:
                checksum = (checksum & 0xFFFF) + (checksum >> 16)

        # operación de negación bit a bit en el checksum.
        checksum = ~checksum

        return checksum & 0xFFFF
