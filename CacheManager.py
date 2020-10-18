import time, datetime
import os
import json
import requests
from functions import *
import concurrent.futures

class CacheManager:
	def __init__(self):
		print("[CacheManager] Cache Manager Initiated.")
		while True:
			print("[CacheManager] Checking if Cached files need updating...")
			to_reload = []
			for level in all_levels.levels + weekly_levels.levels:
				if level.time_to_next_reload() < 0:
					#level.reload_leaderboard()
					to_reload.append(level)
			with concurrent.futures.ThreadPoolExecutor() as executor:
				results = [executor.submit(level.reload_leaderboard) for level in to_reload]
			for global_type in ["all", "regular", "challenge"]:
				for unb in [True, False]:
					get_global_leaderboard(unb, global_type)
					print(f"[CacheManager] Updated Global Leaderboard {global_type},{unb}")
			
			t = min([level.time_to_next_reload() for level in all_levels.levels + weekly_levels.levels])
			
			print(f"[CacheManager] Next Reload in {datetime.timedelta(seconds=int(t))}")
			
			time.sleep(t)