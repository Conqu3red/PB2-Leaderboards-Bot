import requests, json, time, os, datetime, traceback
weekly_url = "https://dfp529wcvahka.cloudfront.net/manifests/weeklyChallenges.json"
download_url = "http://dfp529wcvahka.cloudfront.net/manifests/leaderboards/scores/{0}.json"
download_challenges_url = "https://dfp529wcvahka.cloudfront.net/manifests/leaderboards/challenges/scores/{0}.json"
def round_to(x, base=5):
	return base * round(x/base)

class ShortName:
	def __init__(self, short_name=""):
		"""
		short_name: str
		of the format:
			"1-1c"
			world-level(challenge?)
		"""
		try:
			short_name = short_name.lower()
			if short_name.count("-") == 1:
				self.world = int(short_name.split("-")[0])
				self.level = int(short_name.split("-")[1].replace("c", ""))
			else:
				raise ValueError
			self.is_challenge_level = short_name.endswith("c")
			self.valid = True
		except ValueError:
			self.world = 0
			self.level = 0
			self.is_challenge_level = False
			self.valid = False
	def __str__(self):
		return f"{self.world}-{self.level}{'c' if self.is_challenge_level else ''}"


class AllLevels:
	def __init__(self):
		self.levels = []
		return
		
	def getById(self,id):
		items = [level for level in self.levels if level.id == id]
		if len(items) > 0:
			return items[0]
		else:
			return None
	
	def getByShortName(self,name):
		if not isinstance(name, ShortName):
			name = ShortName(name)
		if not name.valid:
			return
		world, level = name.world, name.level
		challenge = name.is_challenge_level
		try:
			world = int(world)
			level = int(level)
		except ValueError:
			return

		for lvl in self.levels:
			i_world, i_level = lvl.short_name.world, lvl.short_name.level
			i_challenge = lvl.short_name.is_challenge_level
			if int(i_world) == world and int(i_level) == level and challenge == i_challenge:
				return lvl

		return None
	
	def __repr__(self):
		return str(self.levels)

class WeeklyLevels:
	def __init__(self):
		self.levels = []
		self.getByWeek(0) # add items to list
		return
		
	def getByWeek(self,week):
		
		challenge_weeks = {}
		current_time = time.time()
		try:
			cache_last_reloaded = os.path.getmtime(f"data/weeklyChallenges.json")

		except FileNotFoundError:
			cache_last_reloaded = 0
			pass
		if current_time - cache_last_reloaded > 3600: # 8 hours - changed to 1 hour - raz
			r = requests.get(weekly_url)
			with open(f"data/weeklyChallenges.json", "wb") as cache_file:
				cache_file.write(r.content)
			print("[CacheManager] Updated weeklyChallenges")
		with open("data/weeklyChallenges.json") as file:
			data = json.load(file)


		for item in data:
			challenge_weeks[item["week"]] = item
		self.levels = []
		for c,w in challenge_weeks.items():
			self.levels.append(Level(id=w["id"], name=w["title"], isweekly=True, reload_every=3600, week=c, short_name=w["title"], preview=w["preview"]))
		
		for item in self.levels:
			if item.week == week: return item
		return None
	
	def __repr__(self):
		return str(self.levels)


class Level:
	def __init__(self,id=None, name="", short_name=ShortName(),budget=0 , isweekly=False,
	json_folder="data/", extension=".json", reload_every=28000, week=0, preview="", isTest=False):
		self.weekly_prepend = "WC."
		self.base_id = id
		self.name = name
		if not isinstance(short_name, ShortName) and not isweekly:
			short_name = ShortName(short_name)
		self.short_name = short_name
		self.budget = budget
		self.world = None
		self.isweekly = isweekly
		self.json_folder = json_folder
		self.extension = extension
		self.reload_every = reload_every
		self.week = week
		self.preview = preview
		self.isTest = isTest

	
	def reload_leaderboard(self, new_data=None):
		try:
			leaderboard_id = self.id
			if self.isTest: # debug for testing
				data = new_data
			else:
				if not self.isweekly: # Normal level
					url = download_url.format(leaderboard_id)
				else: # Weekly level
					url = download_challenges_url.format(leaderboard_id[3:])
				r = requests.get(url)
				data = r.json()

			old_data_exists = False
			if (os.path.exists(f"data/{leaderboard_id}.json")):
				with open(f"data/{leaderboard_id}.json", "r") as cache_file:
					old_data = json.load(cache_file)
				old_data_exists = True
			else:
				old_data = {}
			#set rankings
			top_history_any = old_data.get("any", {}).get("top_history", [])
			top_history_unbroken = old_data.get("unbroken", {}).get("top_history", [])

			rank_adjusted = {"any":{"top1000":[], "top_history":top_history_any},"unbroken":{"top1000":[], "top_history":top_history_unbroken}}
			for referer in ["any", "unbroken"]:
				#print(referer)
				for rank, score in enumerate(data[referer]["top1000"]):
					score["rank"] = rank+1
					rank_adjusted[referer]["top1000"].append(score)
					if len(rank_adjusted[referer]["top1000"]) > 1: # tie adjustment
						if score["value"] == rank_adjusted[referer]["top1000"][rank-1]["value"]:
							rank_adjusted[referer]["top1000"][-1]["rank"] = rank_adjusted[referer]["top1000"][-2]["rank"]
				#for score in rank_adjusted[referer]["top1000"]:
				#	print(score["rank"], score["value"])
			# timestamps
			now = datetime.datetime.now()
			data = rank_adjusted
			timestamp = datetime.datetime.strftime(now, "%d/%m/%Y-%H:%M")
			# set up top ranks for storage in top_history
			for referer in ["any", "unbroken"]:
				current_top = []
				for score in data[referer]["top1000"]:
					if score["rank"] > 25: break
					score["time"] = timestamp
					current_top.append(score)
				score_ids = [score["id"] for score in data[referer]["top_history"]]
				data[referer]["top_history"] += [score for score in current_top if score["id"] not in score_ids]

			# identify users with removed scores
			for referer in ["any", "unbroken"]:
				user_ids_removed = []
				# detect removed users
				if old_data_exists:
					for old_score in old_data[referer]["top1000"]:
						if old_score["rank"] != 1: break
						found = False
						for r, score in enumerate(data[referer]["top1000"]):
							if old_score["owner"]["id"] == score["owner"]["id"]:
								if old_score["value"] < score["value"]:
									user_ids_removed.append(old_score["owner"]["id"])
								found = True
								break
						if not found: user_ids_removed.append(old_score["owner"]["id"])
				for user_id in user_ids_removed:
					print(f"User with id {user_id} was detected as having a score removed/was banned - fixing top history...")
				# fix top_history
				top_history_fixed = [score for score in data[referer]["top_history"] if score["owner"]["id"] not in user_ids_removed]
				data[referer]["top_history"] = top_history_fixed
			
			# weekly levels don't need oldest history data, should really not compute it at all, but this works
			if self.isweekly:
				rank_adjusted["any"]["top_history"] = []
				rank_adjusted["unbroken"]["top_history"] = []
			
			# save
			with open(f"data/{leaderboard_id}.json", "w") as cache_file:
				json.dump(rank_adjusted, cache_file)
			print(f"[CacheManager] Updated Cache for {leaderboard_id}")
		except Exception as e:
			print(repr(e))
			traceback.print_tb(e.__traceback__)

	def last_reloaded(self):
		try:
			cache_last_reloaded = os.path.getmtime(f"data/{self.id}.json")

		except FileNotFoundError:
			cache_last_reloaded = 0
			pass
		return cache_last_reloaded

	def time_to_next_reload(self):
		last = self.last_reloaded()
		return (last + self.reload_every) - time.time()
	@property
	def id(self):
		return (self.weekly_prepend if self.isweekly else "") + self.base_id
	
	@id.setter
	def id(self, id):
		# when setting the id again just change the base id
		self.base_id = id

	@property
	def leaderboard(self):
		global download_url
		leaderboard_id = self.id
		if self.time_to_next_reload() < 0:
			self.reload_leaderboard()
		try:
			with open(f"data/{leaderboard_id}.json", "rb") as f:
				data = json.load(f)
		except json.decoder.JSONDecodeError:
			# if the data is corrupt, try to fix it
			print(f"[!] Data for {self.id} is corrupt or missing!\n\t- Attempting to force reload data...")
			self.reload_leaderboard()
			try:
				with open(f"data/{leaderboard_id}.json", "rb") as f:
					data = json.load(f)
				print(f"\t- Data reloaded successfully!")
			except json.decoder.JSONDecodeError:
				# This should NEVER happen
				print(f"\t- FAILED! Returning empty structure.")
				data = {"unbroken":{"top1000":[]}, "any":{"top1000":[]}}
		return data

