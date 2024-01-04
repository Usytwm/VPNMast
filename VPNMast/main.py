import config
from vpn import vpn
from User.user import user as us
from Rule.rules import regulation_User, regulation_VLAN
import threading
from udp import UDP


def run_generator(vpn: vpn):
    gen = vpn.run()
    try:
        while True:
            next(gen)
    except StopIteration:
        print("js")
        pass


def help():
    print("help:Show the commands")
    print(
        "start <direccion> <puerto>: Start the VPN with the specified address and port"
    )
    print("stop: Stop the VPN")
    print("create_user <user> <password> <id_vlan>: Create a new user")
    print("remove_user <id>: Remove a user")
    print("get_users: Get all users")
    print(
        "regulation_vlan <rule_name> <id_vlan> <dest_ip> <dest_port>: Restrict a port of an IP to a VLAN"
    )
    print("regulation_vlan <rule_name> <id_vlan> <dest_ip>: Restrict an IP to a VLAN")
    print(
        "regulation_user <rule_name> <id_user> <dest_ip> <dest_port>: Restrict a port of an IP to a user"
    )
    print("regulation_user <rule_name> <id_user> <dest_ip> : Restrict an IP to a user")
    print("remove_rule <id>: Remove a rule")
    print("get_rules: Get all rules")


def handle_input(_vpn: vpn, thread: threading.Thread):
    print("Welcome to VPNMast")
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
            try:
                _vpn.proto.stoped = False
                thread = threading.Thread(target=_vpn.run)
                thread.start()
                continue
            except Exception as e:
                print(e)
                continue
        elif command[0] == "stop":
            if thread is None:
                print("VPN not started\n")
                continue
            _vpn.stop()
            # thread.join()
            thread = None
        elif command[0] == "create_user":
            try:
                user_name = command[1]
                user_password = command[2]
                user_vlan = command[3]
                new_user = us(user_name, user_password, user_vlan)
                _vpn.create_user(new_user)
            except:
                print("Invalid arguments")
        elif command[0] == "remove_user":
            try:
                user_id = int(command[1])
                _vpn.delete_user(user_id)
            except:
                print("Invalid arguments")
        elif command[0] == "get_users":
            try:
                _vpn.show_users()

            except:
                print("Invalid arguments")
        elif command[0] == "exit":
            break

        elif command[0] == "regulation_vlan" and len(command) == 4:
            rule_name = command[1]
            id_vlan = int(command[2])
            dest_ip = command[3]
            new_rule = regulation_VLAN(rule_name, dest_ip, 0, id_vlan)
            _vpn.create_rule(new_rule)

        elif command[0] == "regulation_vlan" and len(command) == 5:
            try:
                rule_name = command[1]
                id_vlan = int(command[2])
                dest_ip = command[3]
                dest_port = int(command[4])
                new_rule = regulation_VLAN(rule_name, dest_ip, dest_port, id_vlan)
                _vpn.create_rule(new_rule)
            except:
                print("Invalid arguments")

        elif command[0] == "regulation_user" and len(command) == 4:
            try:
                rule_name = command[1]
                id_user = int(command[2])
                dest_ip = command[3]
                new_rule = regulation_User(rule_name, dest_ip, 0, id_user)
                _vpn.create_rule(new_rule)
            except:
                print("Invalid arguments")

        elif command[0] == "regulation_user" and len(command) == 5:
            try:
                rule_name = command[1]
                id_user = int(command[2])
                dest_ip = command[3]
                dest_port = int(command[4])
                new_rule = regulation_User(rule_name, dest_ip, dest_port, id_user)
                _vpn.create_rule(new_rule)
            except:
                print("Invalid arguments")

        elif command[0] == "get_rules":
            _vpn.show_rules()

        elif command[0] == "remove_rule":
            rule_id = int(command[1])
            _vpn.delete_rule(rule_id)

        else:
            print("Command not found\n")
            help()


def main():
    # Iniciar la VPN con la dirección y el puerto ingresados
    proto = UDP(config.IP, config.PORT)
    _vpn = vpn(proto=proto)
    thread = None
    input_thread = threading.Thread(target=handle_input, args=(_vpn, thread))
    input_thread.start()
    input_thread.join()


if __name__ == "__main__":
    main()
