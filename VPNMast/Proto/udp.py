import socket
import struct

class UDP():
    def __init__(self, ip, port):
        self._ip = '127.0.0.1' if ip == 'localhost' else ip
        self._port = port
        self.__stop = False

        self.__connection = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        self.__connection.bind((self._ip, self._port))
        self.__connection.setblocking(False)

    def send(self, data, dest_addr):
        dest_ip, dest_port = dest_addr
        dest_ip = '127.0.0.1' if dest_ip == 'localhost' else dest_ip

        data = data.encode('utf-8')

        length = 8 + len(data)
        checksum = 0

        udp_data = struct.pack("!HHHH", self._port, dest_port, length, checksum) + data

        checksum = self.checksum(udp_data)
        udp_header = struct.pack('!HHHH', self._port, dest_port, length, checksum)

        self.__connection.sendto(udp_header + data, (dest_ip, dest_port))

        print(f'UDP data sent to {dest_ip}:{dest_port}\n')

    def run(self):
        while not self.__stop:
            try:
                data, src_addr = self.__connection.recvfrom(1024)

                udp_header = data[:8]
                udp_header = struct.unpack('!HHHH', udp_header)

                src_port, dest_port, length, checksum = udp_header

                if dest_port != self._port:
                    continue

                sender_ip, _ = src_addr

                zero_checksum_header = data[:6] + b'\x00\x00' + data[8:]
                calculated_checksum = checksum( zero_checksum_header + data[8:])

                print(f'UDP data received from {sender_ip}:{dest_port}')

                if checksum != calculated_checksum:
                    print('Corrupted data\n')
                else:
                    data = data[8:].decode('utf-8')
                    print(f'Data: {data}')
                    print(f'Length: {length}, Checksum: {checksum}\n')

                    yield data
            except BlockingIOError:
                continue

    def stop(self):
        self.__stop = True

    @staticmethod
    def checksum(data):
        x = sum(struct.unpack(f'>{len(data)//2}H', data))
        while x > 0xffff:
            x = (x>>16)+(x&0xffff)
        x = 65535 - x
        return x.to_bytes(2, 'big')
