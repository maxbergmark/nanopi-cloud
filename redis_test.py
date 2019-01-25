import redis

r = redis.Redis(
	host = 'elissa-0',
	port = 6379, db = 0)

r.set('foo', 'bar')
print(r.get('foo'))
