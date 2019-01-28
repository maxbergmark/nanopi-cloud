
from redis import Redis
from rq import Queue
import sys

from html import unescape
from lxml import html
import requests

OWN_FILE = 'forty_game_bots.py'
# File where to store the downloaded bots
AUTO_FILE = 'auto_bots.py'
# If you want to use up all your quota & re-download all bots
DOWNLOAD = False
# If you want to ignore a specific user's bots (eg. your own bots): add to list
IGNORE = []
# The API-request to get all the bots
URL = "https://api.stackexchange.com/2.2/questions/177765/answers?page=%s&pagesize=100&order=desc&sort=creation&site=codegolf&filter=!bLf7Wx_BfZlJ7X"


# Make a stack-API request for the n-th page
def req(n):
	req = requests.get(URL % n)
	req.raise_for_status()
	return req.json()

# Pull all the answers via the stack-API
def get_answers():
	n = 1
	api_ans = req(n)
	answers = api_ans['items']
	while api_ans['has_more']:
		n += 1
		if api_ans['quota_remaining']:
			api_ans = req(n)
			answers += api_ans['items']
		else:
			break

	m, r = api_ans['quota_max'], api_ans['quota_remaining']
	if 0.1 * m > r:
		print(" > [WARN]: only %s/%s API-requests remaining!" % (r,m), file=stderr)

	return answers


def download_players():
	players = {}

	for ans in get_answers():
		name = unescape(ans['owner']['display_name'])
		bots = []

		root = html.fromstring('<body>%s</body>' % ans['body'])
		for el in root.findall('.//code'):
			code = el.text
			if re.search(r'^class \w+\(\w*Bot\):.*$', code, flags=re.MULTILINE):
				bots.append(code)

		if not bots:
			print(" > [WARN] user '%s': couldn't locate any bots" % name, file=stderr)
		elif name in players:
			players[name] += bots
		else:
			players[name] = bots

	return players


# Download all bots from codegolf.stackexchange.com
def download_bots():
	print('pulling bots from the interwebs..', file=stderr)
	try:
		players = download_players()
	except Exception as ex:
		print('FAILED: (%s)' % ex, file=stderr)
		exit(1)

	if path.isfile(AUTO_FILE):
		print(' > move: %s -> %s.old' % (AUTO_FILE,AUTO_FILE), file=stderr)
		if path.exists('%s.old' % AUTO_FILE):
			remove('%s.old' % AUTO_FILE)
		rename(AUTO_FILE, '%s.old' % AUTO_FILE)

	print(' > writing players to %s' % AUTO_FILE, file=stderr)
	f = open(AUTO_FILE, 'w+', encoding='utf8')
	f.write('# -*- coding: utf-8 -*- \n')
	f.write('# Bots downloaded from https://codegolf.stackexchange.com/questions/177765 @ %s\n\n' % strftime('%F %H:%M:%S'))
	with open(OWN_FILE, 'r') as bfile:
		f.write(bfile.read()+'\n\n\n# Auto-pulled bots:\n\n')
	for usr in players:
		if usr not in IGNORE:
			for bot in players[usr]:
				f.write('# User: %s\n' % usr)
				f.write(bot+'\n\n')
	f.close()

	print('OK: pulled %s bots' % sum(len(bs) for bs in players.values()))




if __name__ == '__main__':
	from forty_game_controller import *
	from auto_bots import *

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

	# if path.isfile(AUTO_FILE):
		# exec('from %s import *' % AUTO_FILE[:-3])
	# else:
		# exec('from %s import *' % OWN_FILE[:-3])

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

	t0 = time.time()
	jobs = [q.enqueue(run_simulation, i, bots_per_game, games_per_thread, bots, ttl = 1e6, result_ttl=1e6) for i in range(threads)]
	while any(not job.is_finished for job in jobs):
		time.sleep(0.1)
	results = [job.result for job in jobs]

	# results = [run_simulation(i, bots_per_game, games_per_thread, bots) for i in range(threads)]
	# with Pool(threads) as pool:
		# results = pool.starmap(
			# run_simulation, 
			# [(i, bots_per_game, games_per_thread, bots) for i in range(threads)]
		# )
	t1 = time.time()
	if not DEBUG:
		total_bot_stats = [r[0] for r in results]
		total_game_stats = [r[1] for r in results]
		print_results(total_bot_stats, total_game_stats, t1-t0)