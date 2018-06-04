from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from teams.models import Team, Player, FlexMatch
from django.core import serializers
import requests
import json
import time



def index(request):
    headers = { 'X-Riot-Token': 'RGAPI-b0447c72-3b71-4256-9063-fe4fc5ab2479' }
    # r = requests.get('https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-name/wraithcube', headers=headers)
    # r = requests.get('https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/208507406?queue=440&season=11', headers=headers)
    r = requests.get('https://na1.api.riotgames.com/lol/match/v3/matches/2789859686', headers=headers)
    user = r.json()
    return JsonResponse(user)



def list(request):
	data = serializers.serialize("json", Team.objects.all())
	r = json.loads(data)
	return JsonResponse(r, safe=False)
	
def populate(request):
	headers = { 'X-Riot-Token': 'RGAPI-b0447c72-3b71-4256-9063-fe4fc5ab2479' }
	inHeaders = request.META
	myteam = Team.objects.get(name = inHeaders['HTTP_TEAM'])
	players = myteam.player_set.all()
	
	count = 0
	for player in players:
		more_matches = True
		index = 0
		most_recent = player.flexmatch_set.order_by('-timestamp')
		if len(most_recent) > 0:
			most_recent = most_recent[0].timestamp
		else:
			most_recent = 0
		
		while more_matches:
			r = requests.get(f"https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/{player.account_id}?queue=440&season=11&beginIndex={index}", headers=headers).json()
			if len(r['matches']) == 0:
				more_matches = False
			for match in r['matches']:
				
				gameId = match['gameId']
				champion = match['champion']
				season = match['season']
				timestamp = match['timestamp']
				role = match['role']
				lane = match['lane']
				
				if timestamp > most_recent:
					
					details = requests.get(f"https://na1.api.riotgames.com/lol/match/v3/matches/{gameId}", headers=headers).json()
					time.sleep(2)
					
					game_version = details['gameVersion']
					
					participantID = 0
					
					for participant in details['participantIdentities']:
						if (participant['player']['accountId'] == player.account_id):
							participantID = participant['participantId']
						
					win = details['participants'][participantID-1]['stats']['win']
					
					if participantID > 5:
						i = 5
					else:
						i = 0
					
					top = 0
					mid = 0
					jun = 0
					adc = 0
					sup = 0
					
					for j in range(5):
						p_role = details['participants'][j+i]['timeline']['role']
						p_lane = details['participants'][j+i]['timeline']['lane']
						if p_role == 'SOLO' and p_lane == 'TOP':
							top = details['participantIdentities'][j+i]['player']['accountId']
						elif p_role == 'SOLO' and p_lane == 'MIDDLE':
							mid = details['participantIdentities'][j+i]['player']['accountId']
						elif p_role == 'NONE' and p_lane == 'JUNGLE':
							jun = details['participantIdentities'][j+i]['player']['accountId']
						elif p_role == 'DUO_CARRY' and p_lane == 'BOTTOM':
							adc = details['participantIdentities'][j+i]['player']['accountId']
						elif p_role == 'DUO_SUPPORT' and p_lane == 'BOTTOM':
							sup = details['participantIdentities'][j+i]['player']['accountId']
						
					flex = FlexMatch(player = player,
									gameId = gameId,
									champion = champion,
									season = season,
									timestamp = timestamp,
									role = role,
									lane = lane,
									game_version = game_version,
									win = win,
									top = top,
									mid = mid,
									jun = jun,
									adc = adc,
									sup = sup)
					flex.save()

					count += 1
				else:
					more_matches = False
			index += 100

	return JsonResponse({'Games_Created': count})

def add_member(request):
	headers = { 'X-Riot-Token': 'RGAPI-b0447c72-3b71-4256-9063-fe4fc5ab2479' }
	inHeaders = request.META
	name = inHeaders['HTTP_NAME']
	myteam = Team.objects.get(name = inHeaders['HTTP_TEAM'])
	
	r = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-name/{name}", headers=headers).json()

	player = Player(riot_id = r['id'],
					account_id = r['accountId'],
					name = r['name'],
					profile_icon_id = r['profileIconId'],
					revision_date = r['revisionDate'],
					summoner_level = r['summonerLevel'],
					team = myteam)
	
	player.save()
	
	created = {'riot_id': r['id'],
			'account_id': r['accountId'],
			'name': r['name'],
			'profile_icon_id': r['profileIconId'],
			'revision_date': r['revisionDate'],
			'summoner_level': r['summonerLevel'],
			'team': myteam.name}
	
	
	return JsonResponse(created)
	
	

