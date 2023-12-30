import os
import json
from User.user import user as us
from Rule.rule import rule as ru


def get_users():
    path: str = 'users.json'
    
    if not os.path.exists(path):
        return []
    try:
        file = open(path, 'r')
        data = json.load(file)
        file.close()
        return [us.to_user(i) for i in data]
    except:
        print("Error reading file or file is empty")
        return []
def get_user(user_name:str, password:str):
    path: str = 'users.json'
    
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

def get_rules():
    path: str = 'rules.json'
    
    if not os.path.exists(path):
        return []
    try:
        file = open(path, 'r')
        data = json.load(file)
        file.close()
        return [ru.dict_to_rule(i) for i in data]
    except:
        print("Error reading file or file is empty")
        return []
    
