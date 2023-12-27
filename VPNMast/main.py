import config
import socket
from vpn import vpn
from user import user as us
import threading
from Proto.udp import UDP

def run_generator(vpn:vpn):
    gen = vpn.run()
    try:
        while True:
            next(gen)
    except StopIteration:
        pass

def help():
    print("help:Show the commands")
    print("start <direccion> <puerto>: Start the VPN with the specified address and port")
    print("stop: Stop the VPN")
    print("create_user <user> <password> <id_vlan>: Create a new user")
    print("remove_user <id>: Remove a user")
    print("get_user <id>: Get a user")
    print("get_users: Get all users")

thread=None
print('Welcome to VPNMast')
print("Runing...\n")
while True:
    command = input("vpn> ")
    command = command.split(" ")
    if command[0] == "help":
        help()
    elif command[0] == "start":
        if thread is not None:
            print("VPN already started\n")
            continue
        # Iniciar la VPN con la dirección y el puerto ingresados
        proto = UDP(config.IP, config.PORT)
        conection = vpn(proto=proto)
        try:
            thread = threading.Thread(target=run_generator(conection))
            thread.start()
        except Exception as e :
            print(e)
            continue
    elif command[0] == "create_user":
        try:
            user_name = command[1]
            user_password = command[2]
            user_vlan = command[3]
            new_user = us(user_name, user_password, user_vlan)
            vpn.create_user(new_user)
        except:
            print("Invalid arguments")

    elif command[0] == "remove_user":
        try:
            user_id = int(command[1])
            vpn.delete_user(user_id)
        except:
            print("Invalid arguments")
        
    elif command[0] == "get_users":
        try:
            vpn.show_users()
            
        except:
            print("Invalid arguments")
    elif command[0] == "exit":
        break
    else:
        print("Command not found\n")
        help()
    pass