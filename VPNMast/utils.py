import os
import json
from User.user import user as us
from Rule.rule import rule as ru


def get_users():
    path: str = get_dir()
    
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
    