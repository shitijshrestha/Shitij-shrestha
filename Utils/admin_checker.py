from datetime import datetime
import json
import os

ADMIN_FILE = "temp_admins.json"

def is_temp_admin(user_id):
    if not os.path.exists(ADMIN_FILE):
        return False

    with open(ADMIN_FILE, "r") as f:
        try:
            admins = json.load(f)
        except json.JSONDecodeError:
            return False

    expiry = admins.get(str(user_id))
    if not expiry:
        return False

    return datetime.now() < datetime.strptime(expiry, "%Y-%m-%d %H:%M:%S")

def remove_temp_admin(user_id):
    if not os.path.exists(ADMIN_FILE):
        return False

    with open(ADMIN_FILE, "r") as f:
        try:
            admins = json.load(f)
        except json.JSONDecodeError:
            return False

    if str(user_id) in admins:
        del admins[str(user_id)]
        with open(ADMIN_FILE, "w") as f:
            json.dump(admins, f, indent=2)
        return True

    return False