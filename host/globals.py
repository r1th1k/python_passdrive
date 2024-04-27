import json
import os

with open('/Users/rithik-tt0170/Projects/PYTHON_PASSDRIVE/host/config.json') as f:
    config = json.loads(f.read())

volumes = '/Volumes'

local_protected_dir = os.path.join(os.path.expanduser('~'), '.protected')
local_master_dir = os.path.join(os.path.expanduser('~'), '.master')

local_masterpass_file = os.path.join(os.path.expanduser('~'), '.master/master')

pendrive = config['pendrive']

protected_dir = '/Volumes/' + pendrive + '/.protected'
masterpass_dir = '/Volumes/' + pendrive + '/.master'
masterpass_file = os.path.join(masterpass_dir, "master")

tree = "/opt/homebrew/bin/tree"

host_dir = '/Users/rithik-tt0170/Passdrive/host'
setup_path = host_dir + '/setup.py'