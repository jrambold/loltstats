from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from teams.models import Team, Player
from django.core import serializers
import requests



def index(request):
    headers = { 'X-Riot-Token': 'RGAPI-e53f0d2f-6e1c-4b33-aac0-8d1214ffdb77' }
    # r = requests.get('https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-name/wraithcube', headers=headers)
    # r = requests.get('https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/208507406?queue=440&season=11', headers=headers)
    r = requests.get('https://na1.api.riotgames.com/lol/match/v3/matches/2789859686', headers=headers)
    user = r.json()
    return JsonResponse(user)



def list(request):
	data = serializers.serialize("json", Team.objects.all())
	return JsonResponse(data, safe=False)

def add_member(request):
    return HttpResponse('this should add a team member')
