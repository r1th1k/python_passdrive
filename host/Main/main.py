#!/usr/bin/env python3
import json
import logging
import subprocess
import sys
import os
import random
import string
import tkinter as tk
from tkinter import simpledialog
from hashlib import sha256
from Crypto.Cipher import AES
from Crypto.Random import get_random_bytes
from Crypto.Util.Padding import pad, unpad
import base64

def base64_encode(data):
    encoded_bytes = base64.b64encode(data)
    encoded_string = encoded_bytes.decode('utf-8')
    return encoded_string

def base64_decode(encoded_string):
    decoded_bytes = base64.b64decode(encoded_string)
    return decoded_bytes

def encrypt_message(key, message):
    cipher = AES.new(key, AES.MODE_ECB)
    ciphertext = cipher.encrypt(pad(message.encode(), AES.block_size))
    return base64_encode(ciphertext)

def decrypt_message(key, ciphertext):
    cipher = AES.new(key, AES.MODE_ECB)
    decrypted_message = unpad(cipher.decrypt(ciphertext), AES.block_size)
    return decrypted_message.decode()

def create_16_byte_key(input_string):
    input_bytes = input_string.encode()
    while len(input_bytes) < 16:
        input_bytes += input_bytes
    if len(input_bytes) > 16:
        input_bytes = input_bytes[:16]

    return input_bytes

def generator(pass_len, pass_string):
    return ''.join(random.choice(pass_string) for _ in range(pass_len))

def generate_password(pass_len, alph, spcl_ch, num):
    pass_string = ''
    if alph:
        pass_string += string.ascii_letters
    if spcl_ch:
        pass_string += "~`!@#$%^&*()_+-=[]|}{;':/?.>,<;"
    if num:
        pass_string += string.digits

    if not pass_string:
        raise ValueError("At least one of alph, spcl_ch, or num must be True")

    return generator(pass_len, pass_string)

def store_password(domain_name, username, password):
    protected_dir = os.path.join(os.path.expanduser('~'), '.protected')
    
    domain_dir = os.path.join(protected_dir, domain_name)
    
    username_file = os.path.join(domain_dir, username)

    if not os.path.exists(domain_dir):
        os.makedirs(domain_dir)

    if not os.path.exists(username_file):
        with open(username_file, 'w') as f:
            f.write(password)
    else:
        return "USERNAME ALREADY EXISTS ERROR"

def retrieve_password(domain_name, username):
    protected_dir = os.path.join(os.path.expanduser('~'), '.protected')
    
    domain_dir = os.path.join(protected_dir, domain_name)
    
    username_file = os.path.join(domain_dir, username)
    if os.path.exists(domain_dir) and os.path.exists(username_file):
        with open(username_file, 'r') as f:
            password = f.read()
            logging.debug(password)

        return password
    else:
        return ""

def send_message(message):
        encoded_content = json.dumps(message).encode('utf-8')
        
        sys.stdout.buffer.write(len(encoded_content).to_bytes(4, byteorder='little'))
        
        sys.stdout.buffer.write(encoded_content)
        sys.stdout.buffer.flush()

def read_message():
    raw_length = sys.stdin.buffer.read(4)
    if not raw_length:
        sys.exit(0)
    message_length = int.from_bytes(raw_length, byteorder='little')

    message = sys.stdin.buffer.read(message_length).decode('utf-8')
    return json.loads(message)

def check_master_password(master_password):
    masterpass_dir = os.path.join(os.path.expanduser('~'), '.master')
    master_file = os.path.join(masterpass_dir, "master")

    sha_obj = sha256()
    sha_obj.update(master_password.encode())
    hashed_master_password = sha_obj.hexdigest()

    if(os.path.exists(master_file)):   
        with open(master_file, 'r') as f:
            stored_master = f.read()

    else:
        logging.debug("[X] Master password file not found!")
    
    if hashed_master_password == stored_master:
        return True
    else:
        return False

def check_usb_present():
    output = subprocess.run(['diskutil', 'list'], capture_output=True, text=True)
    
    for line in output.stdout.split('\n'):
        if 'external' in line.lower():
            return True
    return False

def main():

    logging.basicConfig(filename='application.log',
                    level=logging.DEBUG,
                    format='%(asctime)s %(message)s',
                    datefmt='%b %M %H:%M:%S')
    logging.debug("[O] App started, Logging Initiated.....")

    if (check_usb_present()):
        logging.debug("[O] USB detected..")
        root = tk.Tk()
        root.withdraw()
        master_password = simpledialog.askstring("Master Password", "Enter your master password:")
        
        if(master_password):
            if(not check_master_password(master_password)):
                logging.debug("[X] Master password not match!")
                exit(0)
            else:
                logging.debug("[O] Master password match!")
        else:
            logging.debug("[X] Master password not received")
            exit(0)

        key = create_16_byte_key(master_password)
        try:
            message = read_message()
            logging.debug("[O] Connection good!, JSON Message received")
        except Exception as e:
            logging.debug("[X] Message not Received or not Found")

        domain_name = message['host']
        username = message['user']
        logging.debug("[O] working on host:{} and user:{}".format(domain_name, username))

        # 1. password retrieve phase
        try:
            password = retrieve_password(domain_name, username)
            if(password != ""):
                logging.debug("[O] Password Found!")
                logging.debug("[O] Decrypting password")
                password = decrypt_message(key, base64_decode(password))
                logging.debug("[O] Password decrypted{}".format(password))
        except Exception as e:
            logging.debug("[X] READ WRITE permission error!:{}".format(e))
            exit(0)

        if password == "":
            # 2. password Generation phase
            logging.debug("[X] Password not found")
            logging.debug("[O] Generating Password")
            password = generate_password(config['passlen'], config["alpha"], config["spcl"], config["num"])
            logging.debug("[O] Password Generated")

            logging.debug("[O] Encrypting password")
            enc_password = encrypt_message(key, password)
            logging.debug("[O] Password encrypted:{}".format(enc_password))

            try:
                logging.debug("[O] storing Password")
                store_password(domain_name, username, enc_password)
                logging.debug("[O] Password Stored")
            except Exception as e:
                logging.debug("[X] Password not stored!\ncheck WRITE PERMISSION!")
                exit(0)

    # 3. message sending to extension phase
        jsonreply = {
            'type': 'autofill_response',
            'user': username,
            'pass': password
        } 

        try:
            logging.debug("[O] Sending Message")
            send_message(jsonreply)
            logging.debug("[O] Message sent")
        except Exception as e:
            logging.debug("[X] Message not sent{}".format(e))

    else:
        logging.debug("[X]USB not found..")
        root = tk.Tk()
        root.withdraw()
        master_password = simpledialog.askstring("USB not found Error","Please insert USB!!")
        exit(0)


if __name__ == '__main__':
    try:
        with open('config.json') as f:
            config = json.loads(f.read())

        main()
    except Exception as e:
        logging.exception(e)
        raise e