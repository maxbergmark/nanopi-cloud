from fabric.api import *

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
def start(ip, password):
	run('cd Documents/nanopi-cloud/forty-game; python3 worker.py %s %s' % (ip, password))