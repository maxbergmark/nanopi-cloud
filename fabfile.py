from fabric.api import *

env.hosts = ['elissa-0', 'elissa-1']
env.key_filename = '~/.ssh/elissa_cluster'

@parallel
def update():
	sudo('apt update')