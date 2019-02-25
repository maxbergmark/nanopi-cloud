from multiprocessing import cpu_count, Process
from redis import Redis
from rq import Connection, Worker

def process():
	c = Redis(host = '192.168.10.200')
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