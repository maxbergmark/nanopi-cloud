from fabric.api import *
import sys

env.hosts = [
	'elissa-0', 
	'elissa-1'
]
env.key_filename = '~/.ssh/id_ecdsa'

@parallel
def update():
	sudo('apt update')

@parallel
def ping():
	run('echo "$(hostname) is up!"')

@parallel
def pull():
	run('cd Documents/nanopi-cloud; git pull')

@parallel
def start():
	run('cd Documents/nanopi-cloud/forty-game; python3 worker.py %s %s' % (sys.argv[1], sys.argv[2]))