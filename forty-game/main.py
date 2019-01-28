
from redis import Redis
from rq import Queue
from forty_game_controller import *
import sys

games = 10000
bots_per_game = 8
threads = 4

for i, arg in enumerate(sys.argv):
	if arg == "-n" and len(sys.argv) > i+1 and sys.argv[i+1].isdigit():
		games = int(sys.argv[i+1])
	if arg == "-b" and len(sys.argv) > i+1 and sys.argv[i+1].isdigit():
		bots_per_game = int(sys.argv[i+1])
	if arg == "-t" and len(sys.argv) > i+1 and sys.argv[i+1].isdigit():
		threads = int(sys.argv[i+1])
	if arg == "-d" or arg == "--download":
		DOWNLOAD = True
	if arg == "-A" or arg == "--ansi":
		ANSI = True
	if arg == "-D" or arg == "--debug":
		DEBUG = True
	if arg == "-h" or arg == "--help":
		print_help()
		quit()
if ANSI:
	print(chr(27) + "[2J", flush =  True)
	print_str(1,3,"")
else:
	print()

if DOWNLOAD:
	download_bots()
	exit() # Before running other's code, you might want to inspect it..

if path.isfile(AUTO_FILE):
	exec('from %s import *' % AUTO_FILE[:-3])
else:
	exec('from %s import *' % OWN_FILE[:-3])

bots = get_all_bots()

if bots_per_game > len(bots):
	bots_per_game = len(bots)
if bots_per_game < 2:
	print("\tAt least 2 bots per game is needed")
	bots_per_game = 2
if games <= 0:
	print("\tAt least 1 game is needed")
	games = 1
if threads <= 0:
	print("\tAt least 1 thread is needed")
	threads = 1
if DEBUG:
	print("\tRunning in debug mode, with 1 thread and 1 game")
	threads = 1
	games = 1

games_per_thread = math.ceil(games / threads)

print("\tStarting simulation with %d bots" % len(bots))
sim_str = "\tSimulating %d games with %d bots per game"
print(sim_str % (games, bots_per_game))
print("\tRunning simulation on %d threads" % threads)
if len(sys.argv) == 1:
	print("\tFor help running the script, use the -h flag")
print()


c = Redis(host = "elissa-0")
q = Queue(connection = c)

jobs = [q.enqueue(run_simulation, (i, bots_per_game, games_per_thread, bots)) for i in range(threads)]
# for i in range(10):
	# jobs.append(q.enqueue(tasks.newkeys, 1024))
while any(not job.is_finished for job in jobs):
	time.sleep(0.1)

results = [job.result for job in jobs]

# with Pool(threads) as pool:
	# t0 = time.time()
	# results = pool.starmap(
		# run_simulation, 
		# [(i, bots_per_game, games_per_thread, bots) for i in range(threads)]
	# )
	# t1 = time.time()
if not DEBUG:
	total_bot_stats = [r[0] for r in results]
	total_game_stats = [r[1] for r in results]
	print_results(total_bot_stats, total_game_stats, t1-t0)