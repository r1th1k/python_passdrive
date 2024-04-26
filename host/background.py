from hashlib import sha256
import os
import subprocess
import shutil
import time

local_protected_dir = os.path.join(os.path.expanduser('~'), '.protected')
local_masterpass_file = os.path.join(os.path.expanduser('~'), '.master/master')


protected_dir = '/Volumes/PASSDRIVE/.protected'
masterpass_dir = '/Volumes/PASSDRIVE/.master'

local_proteced_dir = os.path.join(os.path.expanduser('~'), '.protected')
local_master_dir = os.path.join(os.path.expanduser('~'), '.master')

def check_usb_present():
    output = subprocess.run(['diskutil', 'list'], capture_output=True, text=True)
    
    for line in output.stdout.split('\n'):
        if 'external' in line.lower():
            # logging.debug(line)
            return True
    return False

def copy_local2usb():
    shutil.copy2(local_masterpass_file, masterpass_dir + '/master', follow_symlinks=True)
    shutil.copytree(local_proteced_dir, protected_dir, dirs_exist_ok=True)
    print("local to usb done")

def copy_usb2local():
    shutil.copy2(masterpass_dir + '/master',local_masterpass_file, follow_symlinks=True)
    shutil.copytree( protected_dir,local_proteced_dir, dirs_exist_ok=True)
    print("usb to local done")

def main():
    session = False
    program_path = '/Users/rithik-tt0170/Passdrive/host/setup.py'
    while True:
        if check_usb_present():
            print("USB device connected!")

            if not session:
                if os.path.exists(masterpass_dir) and os.path.exists(protected_dir):
                        os.makedirs(local_master_dir)
                        copy_usb2local()
                        session = True
                        # time.sleep(30)
                
                else:
                    print("[X] Setup not done!!")
                    print("Initiating setup...")
                    subprocess.run(['/usr/bin/python3', program_path])

            while True:
                try:
                    if check_usb_present():
                        if os.path.exists(local_proteced_dir) and os.path.exists(local_master_dir) and os.path.exists(masterpass_dir) and os.path.exists(protected_dir):
                            copy_local2usb()
                            time.sleep(5)

                        if not os.path.exists(protected_dir) and (not os.path.exists(masterpass_dir)):
                            if (not os.path.exists(local_proteced_dir)) and (not os.path.exists(local_master_dir)):
                                time.sleep(10)
                            else:
                                print("No configurations found! Creating new passdrive")
                                os.makedirs(masterpass_dir)
                                copy_local2usb()
                except:
                    if not check_usb_present():
                        print("USB Removed!!")
                        time.sleep(10)
                        shutil.rmtree(local_master_dir)
                        shutil.rmtree(local_proteced_dir)
                        print("Deletion done")
                        session = False
                        break

        else:
            continue

if __name__ == '__main__':
        main()