from hashlib import sha256
import os
import subprocess
import shutil
import time
from globals import *

def check_usb_present():
    output = subprocess.run(['diskutil', 'list'], capture_output=True, text=True)
    
    for line in output.stdout.split('\n'):
        if 'external' in line.lower():
            # logging.debug(line)
            return True
    return False

def copy_local2usb():
    shutil.copy2(local_masterpass_file, masterpass_dir + '/master', follow_symlinks=True)
    shutil.copytree(local_protected_dir, protected_dir, dirs_exist_ok=True)
    print("local to usb done")

def copy_usb2local():
    shutil.copy2(masterpass_dir + '/master',local_masterpass_file, follow_symlinks=True)
    shutil.copytree( protected_dir,local_protected_dir, dirs_exist_ok=True)
    print("usb to local done")

def main():
    session = False
    while True:
        if check_usb_present():
            print("USB device connected!")

            if not session:
                if os.path.exists(masterpass_dir) and os.path.exists(protected_dir):
                        os.makedirs(local_master_dir)
                        copy_usb2local()
                        session = True
                        time.sleep(10)
                
                else:
                    print("[X] Setup not done!!")
                    print("Initiating setup...")
                    subprocess.run(['/usr/bin/python3', setup_path])

            while True:
                try:
                    if check_usb_present():
                        if os.path.exists(local_protected_dir) and os.path.exists(local_master_dir) and os.path.exists(masterpass_dir) and os.path.exists(protected_dir):
                            copy_local2usb()
                            time.sleep(5)
                    else:
                        raise Exception("Pendrive Removed")
                    
                except:
                    if not check_usb_present():
                        print("USB Removed!!")
                        time.sleep(5)
                        shutil.rmtree(local_master_dir)
                        shutil.rmtree(local_protected_dir)
                        print("Deletion done")
                        session = False
                        break

        else:
            continue

if __name__ == '__main__':
        main()