import socket
from utils import parse_ipv4, parse_udp, make_ipv4, make_udp


def start_server():
    # Crea un socket UDP
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    _port = 4321
    _ip = "localhost"
    # Asigna el socket a una dirección y puerto
    server_socket.bind((_ip, _port))

    print(f"The server is listening on {_ip}:{_port}")

    while True:
        # Recibe los datos del cliente
        data, client_address = server_socket.recvfrom(1024)
        proto, src_ip, dst_ip, ip_data = parse_ipv4(data)
        dest_ip, dest_port = client_address
        dest_ip = "127.0.0.1" if dest_ip == "localhost" else dest_ip
        if proto != socket.IPPROTO_UDP:
            continue

        src_port, dest_port, data = parse_udp(ip_data)
        print(
            f"Data received from {client_address[0]}:{client_address[1]} -> {data.decode('utf-8')}"
        )
        try:
            # Calcula el cuadrado del número recibido
            number = int(data.decode("utf-8"))
            square = number**2

            udp_data = make_udp(_port, src_port, str(square).encode("utf-8"))

            ip_data = make_ipv4(
                socket.IPPROTO_UDP,
                "127.0.0.1" if _ip == "localhost" else _ip,
                src_ip,
                udp_data,
            )

            # Envía el cuadrado del número al cliente
            server_socket.sendto(ip_data, client_address)

            print(
                f"Square of the number sent to {client_address[0]}:{client_address[1]} -> {square}"
            )
        except:
            print("Invalid arguments")


if __name__ == "__main__":
    start_server()
