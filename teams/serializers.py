from django.core import serializers
from teams.models import Team

class TeamSerializer(serializers.ModelSerializer):

	class Meta:
		model = Team
		fields = ('name', 'server')
		
