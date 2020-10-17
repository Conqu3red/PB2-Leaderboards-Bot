import requests, json, time, os
weekly_url = "https://dfp529wcvahka.cloudfront.net/manifests/weeklyChallenges.json"
download_url = "http://dfp529wcvahka.cloudfront.net/manifests/leaderboards/scores/{0}.json"
download_challenges_url = "https://dfp529wcvahka.cloudfront.net/manifests/leaderboards/challenges/scores/{0}.json"

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
		world, level = name.split("-")
		challenge = False
		if level.endswith("c"): level = level[:-1]; challenge = True

		world = int(world)
		level = int(level)

		for lvl in self.levels:
			i_world, i_level = lvl.short_name.split("-")
			i_challenge = False
			if i_level.endswith("c"): i_level = i_level[:-1]; i_challenge = True

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
		if current_time - cache_last_reloaded > 28800: # 8 hours
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
	def __init__(self,id=None, name="", short_name="0-0", isweekly=False,
	json_folder="data/", extension=".json", reload_every=28000, week=0, preview=""):
		self.weekly_prepend = "WC."
		self.base_id = id
		self.name = name
		self.short_name = short_name
		self.isweekly = isweekly
		self.json_folder = json_folder
		self.extension = extension
		self.reload_every = reload_every
		self.week = week
		self.preview = preview

	
	def reload_leaderboard(self):
		leaderboard_id = self.id
		if len(leaderboard_id) == 5: # Normal
			url = download_url.format(leaderboard_id)
		elif len(leaderboard_id) == 8:
			url = download_challenges_url.format(leaderboard_id[3:])
		r = requests.get(url)
		with open(f"data/{leaderboard_id}.json", "wb") as cache_file:
			cache_file.write(r.content)
		print(f"[CacheManager] Updated Cache for {leaderboard_id}")
	
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

