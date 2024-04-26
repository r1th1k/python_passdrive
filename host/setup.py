from hashlib import sha256
import os
import subprocess
import json
import getpass

protected_dir = '/Volumes/PASSDRIVE/.protected'
masterpass_dir = '/Volumes/PASSDRIVE/.master'

def save_to_config(config):
    with open("/Users/rithik-tt0170/Passdrive/host/config.json", "w") as json_file:
        json.dump(config, json_file)

def get_config():
    with open("/Users/rithik-tt0170/Passdrive/host/config.json", "r") as json_file:
        config = json.load(json_file)
    return config

def check_master_password(master_password):
    masterpass_dir = '/Volumes/PASSDRIVE/.master'
    master_file = masterpass_dir + '/master'
    master_file = os.path.join(masterpass_dir, "master")

    sha_obj = sha256()
    sha_obj.update(master_password.encode())
    hashed_master_password = sha_obj.hexdigest()

    if(os.path.exists(master_file)):
        with open(master_file, 'r') as f:
            stored_master = f.read()
    else:
        print("Master password file not found!")
    
    if hashed_master_password == stored_master:
        return True
    else:
        return False
    
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
    
def check_usb_present():
    output = subprocess.run(['diskutil', 'list'], capture_output=True, text=True)
    
    for line in output.stdout.split('\n'):
        if 'external' in line.lower():
            return True
    return False


def main():
    if not os.path.exists(protected_dir) and (not os.path.exists(masterpass_dir)):
        print("No configurations found! Creating new passdrive")
        os.makedirs(protected_dir)
        os.makedirs(masterpass_dir)

        masterpass_file = os.path.join(masterpass_dir, "master")
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

        print("Adding common settings to config")
        config = {"passlen": 20, "alpha": True, "spcl": True, "num": True}
        save_to_config(config)
        exit(0)

    if os.path.exists(protected_dir) and (os.path.exists(masterpass_dir)):
        print("Configuration found!")
        master = getpass.getpass("Enter Master Password: ")
        if(not check_master_password(master)):
                print("Wrong master password!")
                exit(0)
   
        choice = int(input("1. Update Master password\n2. Update Website Password\n3. List password\n4. Change Password Default Configs\n\n"))
        print("Enter You Choice: ")
        
        if choice == 1:
            old_master = getpass.getpass("Enter Master Password: ")

            if(not check_master_password(old_master)):
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
            subprocess.check_call(["/opt/homebrew/bin/tree", protected_dir])
        
        if choice == 4:
            config = get_config()
            
            reset = input("Do you want to reset: ")
            if reset!="" or reset!="0" or reset!="no":
                config = {"passlen": 20, "alpha": True, "spcl": True, "num": True}
            else:
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
    if check_usb_present():
        main()
    else:
        print("[X] USB not detected!!")