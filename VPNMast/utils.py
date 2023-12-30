import os
import json
import struct
from ipaddress import ip_address
from User.user import user as us
from Rule.rule import rule as ru


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


def get_users():
    path: str = get_dir()
    
    if not os.path.exists(path):
        return []
    try:
        file = open(path, "r")
        data = json.load(file)
        file.close()
        return [us.to_user(i) for i in data]
    except:
        print("Error reading file or file is empty")
        return []

def get_user(user_name:str, password:str):
    path:str = get_dir()
    if not os.path.exists(path):
        return []
    try:
        file = open(path, 'r')
        data = json.load(file)
        file.close()
        users =  [us.to_user(i) for i in data]
        return next((u for u in users if u.name == user_name and u.pwd == password),None)
    except:
        print("Error reading file or file is empty")
        return None

def get_dir():
    path = ""
    current_directory = os.getcwd()
    if 'users.json' in os.listdir(current_directory):
        path = current_directory+'/users.json'
    else:
        parent_directory = os.path.dirname(current_directory)
        if 'users.json' in os.listdir(parent_directory):
            path = parent_directory+"/users.json"
    return path

def get_rules():
    path: str = "rules.json"

    if not os.path.exists(path):
        return []
    try:
        file = open(path, "r")
        data = json.load(file)
        file.close()
        return [ru.dict_to_rule(i) for i in data]
    except:
        print("Error reading file or file is empty")
        return []


def parse_udp(data):
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


def parse_ipv4(data):
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


def make_udp(src_port, dst_port, body):
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
    check = checksum(udp_data)
    return struct.pack(">HHHH", src_port, dst_port, len(body) + 8, check) + body


def make_ipv4(proto, src_ip, dst_ip, body):
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
    check = checksum(ip_header + body)
    ip_header[10:12] = check.to_bytes(
        2, "big"
    )  # Convierte el checksum en una secuencia de bytes
    return bytes(ip_header + body)
