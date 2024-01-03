import json
from core import Body
from User.user import user
from Rule.rule import rule
from CRUDs.user_crud import user_crud_interface
from CRUDs.rule_crud import rule_crud_interface
import utils
import os
from udp import UDP

class vpn(user_crud_interface, rule_crud_interface):
    def __init__(self, proto: UDP) -> None:
        self.users = utils.get_users()
        self.rules = utils.get_rules()
        self.proto = proto

    def create_user(self, new_user: user):
        if not any(user == new_user for user in self.users):
            new_user.id = len(self.users)
            self.users.append(new_user)
            try:
                self.save_users()
            except:
                print("An error ocurred while creating the user")
                return
            print(f"User {new_user.name} created")
        else:
            print(f"User {new_user.name} already exists")

    def delete_user(self, id: int):
        if any(user.id == id for user in self.users):
            user = self.users[id]
            user_name = user.name
            self.users.remove(user)
            if not len(self.users) == 0:
                for i, user in enumerate(self.users):
                    user.id = i
            try:
                self.save_users()
            except:
                print("An error ocurred while deleting the user")
                return
            print(f"User {user_name} deleted")
        else:
            print(f"User not found")

    def save_users(self):
        path = os.getcwd()+"/users.json"
        file = open(path, 'w+')
        json.dump(self.users,  file, default=lambda o: o.__dict__)
        file.close()

    def run(self):
        for i in self.proto.run():
            try:
                body = vpn_body.dict_to_body(json.loads(i))
                usr = next((i for i in self.users if i.name == body.user and i.pwd==body.password),None)
                if usr == None:
                    print("User not found\n")
                blocked = False
                for i in self.rules:
                    
                    if not i.check(usr, body):
                        print(f'Rule {i.name} blocked to {usr.name} \n')
                        blocked = True
                        break

                if  blocked == False:
                    print("Se envio")
                    self.send(body)
            except Exception as e:
                print(e)
                continue

        
    def send(self, body):
        self.proto.send(body.data, (body.dest_ip, body.dest_port))

    def show_users(self):
        for user in self.users:
            print(f"User: {user.name}")
            print(f"Password: {user.pwd}")
            print(f"Id: {user.id}")
            print("----------------------------------")

    def create_rule(self, new_rule: rule):
        if not any(rule == new_rule for rule in self.rules):
            new_rule.id = len(self.rules)
            self.rules.append(new_rule)
            self.save_rules()
            print(f"Rule {new_rule.name} created")
        else:
            print(f"Rule {new_rule.name} already exists")

    def delete_rule(self, id: int):
        if any(rule.id == id for rule in self.rules):
            rule = self.rules[id]
            rule_name = rule.name
            self.rules.remove(rule)
            if not len(self.rules) == 0:
                for i, rule in enumerate(self.rules):
                    rule.id = i
            self.save_rules()
            print(f"Rule {rule_name} deleted")
        else:
            print(f"Rule not found")

    def save_rules(self):
        path = "rules.json"
        file = open(path, "w+")
        json.dump(
            self.rules,
            file,
            default=lambda o: {
                "name": o.name,
                "category": o.category,
                "ip": o.ip,
                "port": o.port,
                "e_id": o.e_id,
            },
        )
        file.close()

    def show_rules(self):
        for rule in self.rules:
            category = "VLAN Regulation" if rule.category == 0 else "User Regulation"
            e_id = (
                f"id_vlan: {rule.e_id}"
                if rule.category == 0
                else f"user_id: {rule.e_id}"
            )
            print(f"Rule: {rule.name}")
            print(f"Type: {category} {e_id}")
            print(f"Ip: {rule.ip}")
            print(f"Port: {rule.port}")
            print("----------------------------------")

class vpn_body:
    def __init__(self, user: str, password: str, dest_ip: str, dest_port: int, data: str):
        self.user = user
        self.password = password
        self.dest_ip = dest_ip
        self.dest_port = dest_port
        self.data = data

    @staticmethod
    def dict_to_body(dict):
        user = dict['user']
        password = dict['password']
        dest_ip = dict['dest_ip']
        dest_port = dict['dest_port']
        data = dict['data']

        value = vpn_body(user, password, dest_ip, dest_port, data)

        return value
