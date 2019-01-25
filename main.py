from redis import Redis
from rq import Queue
import tasks
import time

c = Redis(host = "elissa-0")
q = Queue(connection = c)

t0 = time.time()
jobs = []
for i in range(100):
	jobs.append(q.enqueue(tasks.newkeys, 1024))
while any(not job.is_finished for job in jobs):
	time.sleep(0.1)
t1 = time.time()

print(t1-t0)