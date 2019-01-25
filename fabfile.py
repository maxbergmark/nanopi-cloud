from fabric.api import *

env.hosts = ['elissa-0', 'elissa-1']
env.key_filename = '~/.ssh/id_ecdsa'

@parallel
def update():
	sudo('apt update')

@parallel
def ping():
	run('echo "$(hostname) is up!"')

@parallel
def pull():
	run('cd Documents/nanopi-cloud;git pull')