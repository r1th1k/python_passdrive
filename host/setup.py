from hashlib import sha256
import os
import subprocess
import json
import getpass
from Main.main import *
from globals import *

def save_to_config(config):
    with open("/Users/rithik-tt0170/Passdrive/host/config.json", "w") as json_file:
        json.dump(config, json_file)

def get_config():
    with open("/Users/rithik-tt0170/Passdrive/host/config.json", "r") as json_file:
        config = json.load(json_file)
    return config

def master_password_setup():
    masterpass_file = os.path.join(masterpass_dir, "master")
    sha_obj = sha256()
    sha_obj_v = sha256()

    master_password = getpass.getpass("Enter Master Password: ")
    sha_obj.update(master_password.encode())
    hashed_master_password = sha_obj.hexdigest()

    master_password_verify = getpass.getpass("Enter Master Password Again: ")
    sha_obj_v.update(master_password.encode())
    hashed_master_password = sha_obj_v.hexdigest()

    if master_password == master_password_verify:
        with open(masterpass_file, 'w') as f:
            f.write(hashed_master_password)
            print("Master Password setup Successfull")

def update_password(domain_name, username, password):
    protected_dir = os.path.join(os.path.expanduser('~'), '.protected')
    
    domain_dir = os.path.join(protected_dir, domain_name)
    
    username_file = os.path.join(domain_dir, username)

    if not os.path.exists(domain_dir):
        print("Domain not found creating domain..")
        os.makedirs(domain_dir)

    if not os.path.exists(username_file):
        print("User not found creating new user")
        with open(username_file, 'w') as f:
            f.write(password)
            print("Password Created!")
    else:
        with open(username_file, 'w') as f:
            f.write(password)
            print("Password Successfully Updated!")

def list_directory(directory):
    try:
        entries = os.listdir(directory)
        for entry in entries:
            print(entry)

    except OSError as e:
        print(f"Error: {e}")

def main():
    if not os.path.exists(protected_dir) and (not os.path.exists(masterpass_dir)):
        print("No configurations found! Creating new config")
        list_directory(volumes)
        pendrive_name = input("Enter Pendrive name: ")
        print("Adding common settings to config")
        config = {"passlen": 20, "alpha": True, "spcl": True, "num": True, "pendrive": pendrive_name}
        save_to_config(config)
        os.makedirs(protected_dir)
        os.makedirs(masterpass_dir)

        sha_obj = sha256()
        sha_obj_v = sha256()

        master_password = input("Enter Master Password: ")
        sha_obj.update(master_password.encode())
        hashed_master_password = sha_obj.hexdigest()

        master_password_verify = input("Enter Master Password Again: ")
        sha_obj_v.update(master_password.encode())
        hashed_master_password = sha_obj_v.hexdigest()

        if master_password == master_password_verify:
            with open(masterpass_file, 'w') as f:
                f.write(hashed_master_password)
                print("Master Password setup Successfull")

        exit(0)

    if os.path.exists(protected_dir) and (os.path.exists(masterpass_dir)):
        print("Configuration found!")
        master = getpass.getpass("Enter Master Password: ")
        if(os.path.exists(masterpass_file)):   
            with open(masterpass_file, 'r') as f:
                stored_master = f.read()
        else:
            logging.debug("[X] Master password file not found!")

        if(not Checks.check_master_password(master, stored_master)):
                print("Wrong master password!")
                exit(0)
   
        print("1. Update Master password\n2. Update Website Password\n3. List password\n4. Change Password Default Configs\n\n")
        choice = int(input("Enter You Choice: "))
        
        if choice == 1:
            old_master = getpass.getpass("Enter Master Password: ")

            if(not Checks.check_master_password(old_master)):
                print("Wrong master password!")
                exit(0)
            else:
                print("New Master Password Setup....")
                master_password_setup()

        if choice == 2:
            domain_name = input("Enter domain name: ")
            user_name = input("Enter user name:")
            password = getpass.getpass("Enter new/updated password: ")
            update_password(domain_name, user_name, password)

        if choice == 3:
            subprocess.check_call([tree, protected_dir])
        
        if choice == 4:
            config = get_config()
            
            reset = input("Do you want to reset: ")
            if reset=="yes":
                config = {"passlen": 20, "alpha": True, "spcl": True, "num": True, "pendrive": pendrive}
            else:
                list_directory(volumes)
                config['pendrive'] = input("Enter Pendrive name: ")
                config['passlen'] = input("Enter Password Length: ")
                print("\n1 => yes\t\t0 or Enter => no")
                config['alpha'] = bool(input("Need Alphabets: "))
                config['spcl'] = bool(input("Need special characters: "))
                config['num'] = bool(input("Need numbers: "))

            save_to_config(config)

    else:
        print("Corrupted File System!")
        exit(0)

if __name__ == '__main__':
    if Checks.check_usb_present():
        main()
    else:
        print("[X] USB not detected!!")