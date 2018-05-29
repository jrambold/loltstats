from django.db import models

class Team(models.Model):
	name = models.CharField(max_length=200)
	server = models.IntegerField(default=0)
	
	def __str__(self):
		return self.name
	
class Player(models.Model):
	username = models.CharField(max_length=200)
	team = models.ForeignKey(Team, on_delete=models.CASCADE)
	
	def __str__(self):
		return self.username