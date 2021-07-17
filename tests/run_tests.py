import unittest
import os
from pprint import pprint

from functions import *

class CheatedScoreTest(unittest.TestCase):
	def test(self):
		d = os.path.join("tests", "cheated_score_test")
		# load test data first
		with open(os.path.join(d, "p1.json")) as f:
			p1 = json.load(f)
		with open(os.path.join(d, "p2.json")) as f:
			p2 = json.load(f)
		
		level = Level(id="temp", name="temp", short_name="0-0", isTest=True)
		with open(f"data/{level.id}.json", "w") as f:
			json.dump(p1, f)

		level.reload_leaderboard(new_data=p2)
		print(level.leaderboard)

		self.assertEqual(len(level.leaderboard["any"]["top_history"]), 1, "top history is not correct")
		self.assertEqual(level.leaderboard["any"]["top_history"][0]["owner"]["display_name"], "user2", "score on top history is not correct")

class SwitchPlaceTest(unittest.TestCase):
	def test(self):
		d = os.path.join("tests", "switch_place_test")
		with open(os.path.join(d, "p1.json")) as f:
			p1 = json.load(f)

		level = Level(id="temp", name="temp", short_name="0-0", isTest=True)
		with open(f"data/{level.id}.json", "w") as f:
			json.dump(p1, f)

		level.reload_leaderboard(new_data=p1)

		all_levels.levels = [level]
		result = get_oldest_scores_leaderboard()
		print("\n\nresult:")
		pprint(result)
		t = datetime.datetime.fromtimestamp(result[0]["time"]).strftime("%d/%m/%Y-%H:%M")
		print(t)
		expected = "24/04/2021-00:20"
		self.assertEqual(t, expected, f"expected '{expected}' but got {t}")

class TieTest(unittest.TestCase):
	def test(self):
		d = os.path.join("tests", "tie_test")
		with open(os.path.join(d, "p1.json")) as f:
			p1 = json.load(f)

		level = Level(id="temp", name="temp", short_name="0-0", isTest=True)
		with open(f"data/{level.id}.json", "w") as f:
			json.dump(p1, f)

		level.reload_leaderboard(new_data=p1)

		all_levels.levels = [level]
		result = get_oldest_scores_leaderboard()
		print("\n\nresult:")
		for s in result:
			s["time"] = datetime.datetime.fromtimestamp(s["time"]).strftime("%d/%m/%Y-%H:%M")
		pprint(result)
		#t = datetime.datetime.fromtimestamp(result[0]["time"]).strftime("%d/%m/%Y-%H:%M")
		#print(t)
		#expected = "24/04/2021-00:20"
		self.assertEqual(result[0]["time"], "24/04/2021-01:00", f"expected '24/04/2021-01:00' but got {result[0]['time']}")
		self.assertEqual(result[1]["time"], "24/04/2021-02:00", f"expected '24/04/2021-02:00' but got {result[1]['time']}")



unittest.main()