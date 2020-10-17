from level import *

# populate AllLevels with data
with open("level_names.txt", "r") as f:
	level_data = f.read().splitlines()

levels = AllLevels()
for i in level_data:
	data = i.split(":")
	levels.levels.append(Level(id=data[1],name=data[2],short_name=data[0]))

# populate WeeklyLevels with data
weekly_levels = WeeklyLevels()