class Level:
	def __init__(self,id=None, name="", isweekly=False, json_folder="data/", extension=".json"):
		self.weekly_prepend = "WC."
		self.base_id = id
		self.name = name
		self.isweekly = isweekly
		self.json_folder = json_folder
		self.extension = extension

	
	@property
	def id(self):
		return (self.weekly_prepend if self.isweekly else "") + self.base_id
	
	@id.setter
	def id(self, id):
		# when setting the id again just change the base id
		self.base_id = id



a = Level(id="ABCDE",name="1-1")
