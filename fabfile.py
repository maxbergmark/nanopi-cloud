from fabric import Connection
from redis import Redis

hosts = ['elissa-0', 'elissa-1']
connections = [Connection(host) for host in hosts]
