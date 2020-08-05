import json
import os
from datetime import *
import time
#print(os.path.getmtime("data/collated.json"))
#print(time.time())
with open("data/collated.json") as data:
	json_data = json.load(data)
#print(json_data.keys())
print(len(json_data.keys()))
identifiers = {
"1": ["mAp2V", "NAgrb", "Bbm2A", "0A5Zn", "JbOmn", "aVeaV", "5VlRA", "gnR7V", "7b7xA", "WAGoA", "ObqMb", "EAaRn", "Xb3Ob", "1nXeV", "EABGn", "6Vw5A"],   # World 1
"2": ["zA0Mn", "kb2wA", "gb1Kn", "ZAoeV", "MAr3n", "QVYRb", "JnZ2n", "PV4Qb", "yb8Pb", "gnyrV", "MAEoV", "qn9JV", "5AWzb", "MV6DA", "1nQen", "bmw2n"],    #World 2
"3": ["jnL9V", "vAMDb", "lnKkn", "bdjrn", "JbDPb", "mnkRA", "Ap22V", "abx5A", "5VJBV", "zAvPV", "JVPon", "ZbjWA", "XVzGb", "A5QZA", "ObNoA", "AgXrn"],    #World 3
"4": ["nk2rA", "nKv3A", "bje7V", "b2qZV", "VPllV", "nyl7A", "VY39A", "Av89V", "bxeQA", "AW4kn", "bDDrb", "nQlOA", "nZLOb", "n9ZBV", "AM8vb", "V6BNV"],    #World 4
"1c": ["AW7zA", "bq7Mn", "Aa7RV", "Ao2eb", "nXLen", "Vw85b", "V6qDn", "nK8kV", "b33Ob", "A0rMV", "nZ32V", "VY4Rn", "ABDGV", "AEBon", "b1qKb", "n9dJA"],    #World 1c
"2c": ["VzoGb", "nQOeb", "b2WwA", "nyXrA", "AMmDA", "VJDBA", "AvMPb", "bN5oV", "bDzPn", "bxN5n", "nklRV", "VPgon", "b83PV", "bjMWV", "nLm9V", "V4LQV"],    #World 2c
"3c": ["Vezab", "Arl3V", "bdarA", "A5GZV", "bqYMb", "AGDon", "ApQ9n", "ApQ2n", "AgrJb", "bdaqA", "Agrrb", "b7lxA", "bmK2n", "Vl5Rb", "bOpmA", "nRM7A"],    #World 3c
"4c": ["b7ljA", "bOpaA", "Aa5OA", "VwMpA", "A0ZaV", "bqYob", "A5GJV", "b3WDb", "nXZzb", "nRM8A", "AGD6n", "AB19b", "Vez1b", "bmK9n", "AoqpV", "Vl5gb"]     #World 4c
}
#print(identifiers.values())
new_l = []
new = 0
for ID in json_data.keys():
	found = False
	for world in identifiers.values():
		for l_id in world:
			if ID == l_id:
				found = True
				break
	if not found:
		new += 1
		new_l.append(ID)
print(new_l)
print(new)

#print(len(world_5_leaderboards))
#new_levels = len(world_5_leaderboards)
