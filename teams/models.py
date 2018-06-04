from django.db import models

class Team(models.Model):
	name = models.CharField(max_length=200)
	server = models.IntegerField(default=0)

	def __str__(self):
		return self.name

class Player(models.Model):
	riot_id = models.IntegerField()
	account_id = models.IntegerField()
	name = models.CharField(max_length=200)
	profile_icon_id = models.IntegerField()
	revision_date = models.IntegerField()
	summoner_level = models.IntegerField()
	team = models.ForeignKey(Team, on_delete=models.CASCADE)

	def __str__(self):
		return self.name

class FlexMatch(models.Model):
	player = models.ForeignKey(Player, on_delete=models.CASCADE)
	gameId = models.IntegerField()
	champion = models.IntegerField()
	season = models.IntegerField()
	timestamp = models.IntegerField()
	role = models.CharField(max_length=200)
	lane = models.CharField(max_length=200)
	game_version = models.CharField(max_length=200)
	win = models.BooleanField()
	top = models.IntegerField(default=0)
	mid = models.IntegerField(default=0)
	jun = models.IntegerField(default=0)
	adc = models.IntegerField(default=0)
	sup = models.IntegerField(default=0)

	def __str__(self):
		return f"{self.player} {self.gameId}"