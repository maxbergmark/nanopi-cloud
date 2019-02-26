from multiprocessing import cpu_count, Process
from redis import Redis
from rq import Connection, Worker
import sys

def process():
	password = sys.argv[1]
	c = Redis(host = '127.0.0.1', port = 6399, password = password)
	w = Worker(['default'], connection = c)
	w.work()

if __name__ == '__main__':
	n = cpu_count()
	ps = []
	for i in range(n):
		p = Process(target = process, args = ())
		p.start()
		ps.append(p)
	for p in ps:
		p.join()