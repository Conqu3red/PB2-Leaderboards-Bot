import time, datetime
import os
import json
import requests
# download_url refers to the location of the leaderboard files
download_url = "http://dfp529wcvahka.cloudfront.net/manifests/leaderboards/scores/{0}.json"
weekly_url = "https://dfp529wcvahka.cloudfront.net/manifests/weeklyChallenges.json"
download_challenges_url = "https://dfp529wcvahka.cloudfront.net/manifests/leaderboards/challenges/scores/{0}.json"
identifiers = {
"1":  ["mAp2V","NAgrb","Bbm2A","0A5Zn","JbOmn","aVeaV","5VlRA","gnR7V","7b7xA","WAGoA","ObqMb","EAaRn","Xb3Ob","1nXeV","EABGn","6Vw5A"], #World 1
"2":  ["zA0Mn","kb2wA","gb1Kn","ZAoeV","MAr3n","QVYRb","JnZ2n","PV4Qb","yb8Pb","gnyrV","MAEoV","qn9JV","5AWzb","MV6DA","1nQen","bmw2n"], #World 2
"3":  ["jnL9V","vAMDb","lnKkn","bdjrn","JbDPb","mnkRA","Ap22V","abx5A","5VJBV","zAvPV","JVPon","ZbjWA","XVzGb","A5QZA","ObNoA","AgXrn"], #World 3
"4":  ["nk2rA","nKv3A","bje7V","b2qZV","VPllV","nyl7A","VY39A","Av89V","bxeQA","AW4kn","bDDrb","nQlOA","nZLOb","n9ZBV","AM8vb","V6BNV"], #World 4
"5":  ["AGDKo","nRM67","AoqEe","bqYEM","b7l7x","Aa58R","b3WOO","VwMk5","AB1QG","nXZMe","A0ZgM","AEOYo","b1WmK","nKvxk","VY3MR","nZLM2"], #World 5
"1c": ["AW7zA","bq7Mn","Aa7RV","Ao2eb","nXLen","Vw85b","V6qDn","nK8kV","b33Ob","A0rMV","nZ32V","VY4Rn","ABDGV","AEBon","b1qKb","n9dJA"], #World 1c
"2c": ["VzoGb","nQOeb","b2WwA","nyXrA","AMmDA","VJDBA","AvMPb","bN5oV","bDzPn","bxN5n","nklRV","VPgon","b83PV","bjMWV","nLm9V","V4LQV"], #World 2c
"3c": ["Vezab","Arl3V","bdarA","A5GZV","bqYMb","AGDon","ApQ9n","ApQ2n","AgrJb","bdaqA","Agrrb","b7lxA","bmK2n","Vl5Rb","bOpmA","nRM7A"], #World 3c
"4c": ["b7ljA","bOpaA","Aa5OA","VwMpA","A0ZaV","bqYob","A5GJV","b3WDb","nXZzb","nRM8A","AGD6n","AB19b","Vez1b","bmK9n","AoqpV","Vl5gb"], #World 4c
"5c": ["VJGKB","AgrJr","ApQj2","V6BRD","nLar9","bx3E5","VzJ2G","nQm4e","bdaJr","Av8NP","bNdLo","b2Z5w","ArdM3","V45eQ","VPeKo","b8zGP"], #World 5c
"6":  ["bOeMR","A5XOx","nR5Re","bm2OL","b7WRR","Vl2Wp","VeDY5","AGvLD","AaE79","bqe7e","b3Y34","nXvLa","ABND7","Vwa8y","A0QrO","Aor26"]	 #World 6
}


class CacheManager:
	def __init__(self):
		print("[CacheManager] Cache Manager Initiated.")
		pass
		self.levels_last_refreshed = {}
		self.gap = 28800 # seconds
		self.challenge_weeks = {}
		self.get_weekly_challenge_ids()
		self.get_all_files_last_refresh()
		while True:
			print("[CacheManager] Checking if Cached files need updating...")
			for item in self.levels_last_refreshed.items():
				if item[1] > self.gap:
					self.refresh_data(item[0])
			self.get_weekly_challenge_ids()
			self.get_all_files_last_refresh()
			print(f"[CacheManager] Next Reload in {datetime.timedelta(seconds=int(max( self.gap - min(list(self.levels_last_refreshed.values())), 0)))}")
			time.sleep( max( self.gap - min(list(self.levels_last_refreshed.values())) ,0)  )
	def get_all_files_last_refresh(self,override=False):
		global download_url
		for world in identifiers.values():
			for leaderboard_id in world:
				current_time = time.time()
				try:
					cache_last_reloaded = os.path.getmtime(f"data/{leaderboard_id}.json")
					
				except FileNotFoundError:
					cache_last_reloaded = 0
					pass
				self.levels_last_refreshed[leaderboard_id] = current_time - cache_last_reloaded
	def refresh_data(self, leaderboard_id):
		global download_url
		if len(leaderboard_id) == 5: # Normal
			url = download_url.format(leaderboard_id)
		elif len(leaderboard_id) == 8:
			url = download_challenges_url.format(leaderboard_id[3:])
		r = requests.get(url)
		with open(f"data/{leaderboard_id}.json", "wb") as cache_file:
			cache_file.write(r.content)
		print(f"[CacheManager] Updated Cache for {leaderboard_id}")
	def get_weekly_challenge_ids(self):
		r = requests.get(weekly_url)
		data = json.loads(r.content)
		identifiers["WC"] = []
		for item in data:
			identifiers["WC"].append("WC." + item["id"])
			self.challenge_weeks[item["week"]] = item["id"]