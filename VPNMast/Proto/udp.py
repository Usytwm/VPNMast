import socket
import struct
from ipaddress import ip_address
import os

class UDP():
    def __init__(self, ip, port):
        self._ip = '127.0.0.1' if ip == 'localhost' else ip
        self._port = port
        self.__stop = False

        # self.__connection = socket.socket(socket.AF_INET,  socket.SOCK_RAW, socket.IPPROTO_UDP)
        self.__connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)

        self.__connection.bind((self._ip, self._port))
        

    def parse_udp(self, data):
        src_port, dst_port = struct.unpack('>HH', data[:4])
        return src_port, dst_port, data[8:]

    def parse_ipv4(self, data):
        ihl = data[0]&0x0f
        length = int.from_bytes(data[2:4], 'big')
        proto = data[9]
        src_ip = ip_address(data[12:16])
        dst_ip = ip_address(data[16:20])
        body = data[ihl<<2:length]
        return proto, src_ip, dst_ip, body
    
    def make_udp(self, src_port, dst_port, body):
        udp_data = struct.pack('>HHHH', src_port, dst_port, len(body)+8, 0) + body
        checksum = self.checksum(udp_data)
        return struct.pack('>HHHH', src_port, dst_port, len(body)+8, checksum) + body

    def make_ipv4(self, proto, src_ip, dst_ip, body):
        ip_header = bytearray(struct.pack('>BxH2s2xBB2x4s4s', 0x45, len(body)+20, os.urandom(2), 64,
            proto, ip_address(src_ip).packed, ip_address(dst_ip).packed))
        checksum = self.checksum(ip_header + body)
        ip_header[10:12] = checksum.to_bytes(2, 'big')  # Convierte el checksum en una secuencia de bytes
        return bytes(ip_header + body)
    
    
    def send(self, data, dest_addr):
        dest_ip, dest_port = dest_addr
        dest_ip = '127.0.0.1' if dest_ip == 'localhost' else dest_ip

        data = data.encode('utf-8')

        udp_data = self.make_udp(self._port, dest_port, data)

        ip_data = self.make_ipv4(socket.IPPROTO_UDP, self._ip, dest_ip, udp_data)
       
        self.__connection.sendto(ip_data, (dest_ip, dest_port))

        print(f'UDP data sent to {dest_ip}:{dest_port}\n')

    def run(self):
        # print('server iniciado')
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
                received_checksum = struct.unpack('>H', ip_data[6:8])[0]

                # Crea un encabezado UDP con el checksum establecido en 0
                zero_checksum_header = ip_data[:6] + b'\x00\x00' + ip_data[8:]

                # Calcula el checksum
                calculated_checksum = self.checksum(zero_checksum_header)

                print(f'UDP data received from {sender_ip}:{src_port}')
                
                if received_checksum != calculated_checksum:
                   print('Corrupted data\n')
                else:
                    data = udp_data.decode('utf-8')
                    print(f'Data: {data}\n')

                yield data
                
            except BlockingIOError:
                continue

    def stop(self):
        self.__stop = True

    @staticmethod
    def checksum(data):
        checksum = 0
        for i in range(0, len(data), 2):
            if i + 1 < len(data):
                checksum += (data[i] << 8) + data[i+1]
            else:
                checksum += data[i]
            while checksum >> 16:
                checksum = (checksum & 0xFFFF) + (checksum >> 16)

        checksum = ~checksum

        return checksum & 0xFFFF
        # x = sum(struct.unpack(f'>{len(data)//2}H', data))
        # while x > 0xffff:
        #     x = (x>>16)+(x&0xffff)
        # x = 65535 - x
        # return x


