
class user:
    def __init__(self, name:str, pwd :str,id_vlan:int) -> None:
        self.name = name
        self.pwd = pwd
        self.id_vlan = id_vlan
        self.id = 0
        pass

    @staticmethod
    def to_user(dict:dict):
        parsed_user = user(dict['name'],dict['pwd'],dict['id_vlan'])
        parsed_user.id = dict['id']
        return parsed_user
    
    def __eq__(self, other):
        if isinstance(other, user):
            return self.name == other.name and self.pwd == other.pwd
        return False
    
