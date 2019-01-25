from fabric.api import *

env.hosts = ['elissa-0', 'elissa-1']

@parallel
def update():
	sudo('apt update')