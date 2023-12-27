import json
from core import Body
from user import user
from user_crud import user_crud_interface
import utils
from Proto.udp import UDP

class vpn(user_crud_interface):
   
    def __init__ (self,proto:UDP) -> None:
        self.users = utils.get_users()
        self.proto=proto

    def create_user(self, new_user:user):
        if not any(user == new_user for user in self.users):
            new_user.id = len(self.users)
            self.users.append(new_user)
            self.save_users()
            print(f"User {new_user.name} created")
        else:
            print(f"User {new_user.name} already exists")  

    def delete_user(self, id:int):
        if any(user.id == id for user in self.users):
            user = self.users[id]
            user_name = user.name
            self.users.remove(user)
            if not len(self.users)==0:
                 for i, user in enumerate(self.users):
                    user.id = i
            self.save_users()
            print(f"User {user_name} deleted")
        else:  
            print(f"User not found")
            
    def save_users(self):
        path = 'users.json'
        file = open(path, 'w+')
        json.dump(self.users,  file, default=lambda o: o.__dict__)
        file.close()
    
    def run(self):
        for i in self.proto.run():
            try:
                body = Body.dict_to_body(json.loads(i))
                self.send(body)
            except Exception as e:
                print(e)
                continue
    
    def send(self,body:Body):
        self.proto.send(body.data, (body.dest_ip, body.dest_port))
    
    def show_users(self):
        for user in self.users:
            print(f"User: {user.name}")
            print(f"Password: {user.pwd}")
            print(f"Id: {user.id}")
            print("----------------------------------")


# user1 = user("a", "a", 1)
# vpn.create_user(user1)
# user2 = user("b", "b", 2)
# vpn.create_user(user2)
# vpn.show_users()
# user2 = user("b", "b", 2)
# vpn.create_user(user2)
# user3 = user("c", "c", 3)
# vpn.create_user(user3)
# user4 = user("d", "d", 4)
# vpn.create_user(user4)
# user5 = user("e", "e", 5)
# vpn.create_user(user5)
#vpn.delete_user(0)