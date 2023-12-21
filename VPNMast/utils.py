import os
import json
from user import user as us

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
        print("Error reading file of file empty")
        return []
    