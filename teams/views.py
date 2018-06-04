from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from teams.models import Team, Player, FlexMatch
from django.core import serializers
import requests
import json
import time

def headers():
	return { 'X-Riot-Token': 'RGAPI-b0447c72-3b71-4256-9063-fe4fc5ab2479' }

def index(request):
    return JsonResponse({'Hello': 'World'})


#lists all teams
def list(request):
	data = serializers.serialize("json", Team.objects.all())
	r = json.loads(data)
	return JsonResponse(r, safe=False)

#takes headers team
def populate(request):
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
			r = requests.get(f"https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/{player.account_id}?queue=440&season=11&beginIndex={index}", headers=headers()).json()
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
					
					details = requests.get(f"https://na1.api.riotgames.com/lol/match/v3/matches/{gameId}", headers=headers()).json()
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

#takes headers team and name
def add_member(request):
	inHeaders = request.META
	name = inHeaders['HTTP_NAME']
	myteam = Team.objects.get(name = inHeaders['HTTP_TEAM'])
	
	r = requests.get(f"https://na1.api.riotgames.com/lol/summoner/v3/summoners/by-name/{name}", headers=headers()).json()

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
	
#takes headers team and min
def best_by_position(request):
	inHeaders = request.META
	if 'HTTP_MIN' in set(inHeaders):
		min_games = int(inHeaders['HTTP_MIN'])
	else:
		min_games = 0
	
	myteam = Team.objects.get(name = inHeaders['HTTP_TEAM'])
	
	player = myteam.player_set.all()[1]
	
	top_total = 0
	top_wins = 0
	top_player = 'None'

	mid_total = 0
	mid_wins = 0
	mid_player = 'None'

	jun_total = 0
	jun_wins = 0
	jun_player = 'None'

	adc_total = 0
	adc_wins = 0
	adc_player = 'None'

	sup_total = 0
	sup_wins = 0
	sup_player = 'None'
	
	players = myteam.player_set.all()
	
	for player in players:
		current_top_wins = player.flexmatch_set.filter(top=player.account_id).filter(win=True).count()
		current_top_total = player.flexmatch_set.filter(top=player.account_id).count()
		if percent(top_wins, top_total) < percent(current_top_wins, current_top_total) and current_top_total >= min_games:
			top_wins = current_top_wins
			top_total = current_top_total
			top_player = player.name

		current_mid_wins = player.flexmatch_set.filter(mid=player.account_id).filter(win=True).count()
		current_mid_total = player.flexmatch_set.filter(mid=player.account_id).count()
		if percent(mid_wins, mid_total) < percent(current_mid_wins, current_mid_total) and current_mid_total >= min_games:
			mid_wins = current_mid_wins
			mid_total = current_mid_total
			mid_player = player.name
			
		current_jun_wins = player.flexmatch_set.filter(jun=player.account_id).filter(win=True).count()
		current_jun_total = player.flexmatch_set.filter(jun=player.account_id).count()
		if percent(jun_wins, jun_total) < percent(current_jun_wins, current_jun_total) and current_jun_total >= min_games:
			jun_wins = current_jun_wins
			jun_total = current_jun_total
			jun_player = player.name
			
		current_adc_wins = player.flexmatch_set.filter(adc=player.account_id).filter(win=True).count()
		current_adc_total = player.flexmatch_set.filter(adc=player.account_id).count()
		if percent(adc_wins, adc_total) < percent(current_adc_wins, current_adc_total) and current_adc_total >= min_games:
			adc_wins = current_adc_wins
			adc_total = current_adc_total
			adc_player = player.name
			
		current_sup_wins = player.flexmatch_set.filter(sup=player.account_id).filter(win=True).count()
		current_sup_total = player.flexmatch_set.filter(sup=player.account_id).count()
		if percent(sup_wins, sup_total) < percent(current_sup_wins, current_sup_total) and current_sup_total >= min_games:
			sup_wins = current_sup_wins
			sup_total = current_sup_total
			sup_player = player.name
	
	
	best_group = {'top': {'name': top_player, 'percent': percent(top_wins, top_total), 'wins': top_wins, 'losses': (top_total-top_wins), 'total': top_total},
				'mid': {'name': mid_player, 'percent': percent(mid_wins, mid_total), 'wins': mid_wins, 'losses': (mid_total-mid_wins), 'total': mid_total},
				'jun': {'name': jun_player, 'percent': percent(jun_wins, jun_total), 'wins': jun_wins, 'losses': (jun_total-jun_wins), 'total': jun_total},
				'adc': {'name': adc_player, 'percent': percent(adc_wins, adc_total), 'wins': adc_wins, 'losses': (adc_total-adc_wins), 'total': adc_total},
				'sup': {'name': sup_player, 'percent': percent(sup_wins, sup_total), 'wins': sup_wins, 'losses': (sup_total-sup_wins), 'total': sup_total}}
				
	return JsonResponse(best_group)

def percent(portion, full):
	if full == 0:
		return 0
	return portion/full*100
