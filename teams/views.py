from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from teams.models import Team, Player, FlexMatch, SoloMatch
from django.core import serializers
import requests
import json
import time
import os
import django_rq

#Endpoint reached test response

def index(request):
    return JsonResponse({'Hello': 'World'})

#add and get teams

def list(request):
	data = serializers.serialize("json", Team.objects.all())
	r = json.loads(data)
	return JsonResponse(r, safe=False)

def add_team(request):
	inHeaders = request.META
	name = inHeaders['HTTP_TEAM']

	team = Team(name = name)
	team.save()

	created = {'Team': name}
	return JsonResponse(created)

def delete_team(request):
	inHeaders = request.META
	name = inHeaders['HTTP_TEAM']
	myteam = Team.objects.get(name = name)

	myteam.delete()

	return JsonResponse({'Deleted_Team': name})

#add and get team members

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

	django_rq.enqueue(populate_background, inHeaders['HTTP_TEAM'])
	django_rq.enqueue(solo_populate_background, name)

	created = {'riot_id': r['id'],
			'account_id': r['accountId'],
			'name': r['name'],
			'profile_icon_id': r['profileIconId'],
			'revision_date': r['revisionDate'],
			'summoner_level': r['summonerLevel'],
			'team': myteam.name}


	return JsonResponse(created)

def get_team_members(request):
	inHeaders = request.META
	myteam = Team.objects.get(name = inHeaders['HTTP_TEAM'])
	data = serializers.serialize("json", myteam.player_set.all())
	r = json.loads(data)
	return JsonResponse(r, safe=False)

def delete_member(request):
	inHeaders = request.META
	name = inHeaders['HTTP_NAME']
	myplayer = Player.objects.get(name = name)

	myplayer.delete()

	return JsonResponse({'Deleted_Player': name})

#Team Stats

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

def custom_team(request):
	inHeaders = request.META

	top = False
	mid = False
	jun = False
	adc = False
	sup = False

	if 'HTTP_TOP' in set(inHeaders):
		top = Player.objects.filter(name=inHeaders['HTTP_TOP'])[0]
		exists = top

	if 'HTTP_MID' in set(inHeaders):
		mid = Player.objects.filter(name=inHeaders['HTTP_MID'])[0]
		exists = mid

	if 'HTTP_JUN' in set(inHeaders):
		jun = Player.objects.filter(name=inHeaders['HTTP_JUN'])[0]
		exists = jun

	if 'HTTP_ADC' in set(inHeaders):
		adc = Player.objects.filter(name=inHeaders['HTTP_ADC'])[0]
		exists = adc

	if 'HTTP_SUP' in set(inHeaders):
		sup = Player.objects.filter(name=inHeaders['HTTP_SUP'])[0]
		exists = sup

	games = exists.flexmatch_set.all()
	if top:
		games = games.filter(top=top.account_id)
	if mid:
		games = games.filter(mid=mid.account_id)
	if jun:
		games = games.filter(jun=jun.account_id)
	if adc:
		games = games.filter(adc=adc.account_id)
	if sup:
		games = games.filter(sup=sup.account_id)

	total = games.count()
	wins = games.filter(win=True).count()

	group = {'percent': percent(wins, total), 'wins': wins, 'losses': (total-wins), 'total': total}

	return JsonResponse(group)

#Combo Stat Methods

def solo_stats(request):
	inHeaders = request.META
	player = Player.objects.get(name = inHeaders['HTTP_NAME'])

	total = player.solomatch_set.count()
	wins = player.solomatch_set.filter(win=True).count()

	top_wins = player.solomatch_set.filter(top=player.account_id).filter(win=True).count()
	top_total = player.solomatch_set.filter(top=player.account_id).count()

	mid_wins = player.solomatch_set.filter(mid=player.account_id).filter(win=True).count()
	mid_total = player.solomatch_set.filter(mid=player.account_id).count()

	jun_wins = player.solomatch_set.filter(jun=player.account_id).filter(win=True).count()
	jun_total = player.solomatch_set.filter(jun=player.account_id).count()

	adc_wins = player.solomatch_set.filter(adc=player.account_id).filter(win=True).count()
	adc_total = player.solomatch_set.filter(adc=player.account_id).count()

	sup_wins = player.solomatch_set.filter(sup=player.account_id).filter(win=True).count()
	sup_total = player.solomatch_set.filter(sup=player.account_id).count()

	stats = {'total': {'percent': percent(wins, total), 'wins': wins, 'losses': (total-wins), 'total': total},
			'top': {'percent': percent(top_wins, top_total), 'wins': top_wins, 'losses': (top_total-top_wins), 'total': top_total},
			'mid': {'percent': percent(mid_wins, mid_total), 'wins': mid_wins, 'losses': (mid_total-mid_wins), 'total': mid_total},
			'jun': {'percent': percent(jun_wins, jun_total), 'wins': jun_wins, 'losses': (jun_total-jun_wins), 'total': jun_total},
			'adc': {'percent': percent(adc_wins, adc_total), 'wins': adc_wins, 'losses': (adc_total-adc_wins), 'total': adc_total},
			'sup': {'percent': percent(sup_wins, sup_total), 'wins': sup_wins, 'losses': (sup_total-sup_wins), 'total': sup_total}}

	return JsonResponse(stats)

def solo(request):
	inHeaders = request.META
	player = Player.objects.get(name = inHeaders['HTTP_NAME'])

	total = player.flexmatch_set.count()
	wins = player.flexmatch_set.filter(win=True).count()

	top_wins = player.flexmatch_set.filter(top=player.account_id).filter(win=True).count()
	top_total = player.flexmatch_set.filter(top=player.account_id).count()

	mid_wins = player.flexmatch_set.filter(mid=player.account_id).filter(win=True).count()
	mid_total = player.flexmatch_set.filter(mid=player.account_id).count()

	jun_wins = player.flexmatch_set.filter(jun=player.account_id).filter(win=True).count()
	jun_total = player.flexmatch_set.filter(jun=player.account_id).count()

	adc_wins = player.flexmatch_set.filter(adc=player.account_id).filter(win=True).count()
	adc_total = player.flexmatch_set.filter(adc=player.account_id).count()

	sup_wins = player.flexmatch_set.filter(sup=player.account_id).filter(win=True).count()
	sup_total = player.flexmatch_set.filter(sup=player.account_id).count()

	stats = {'total': {'percent': percent(wins, total), 'wins': wins, 'losses': (total-wins), 'total': total},
			'top': {'percent': percent(top_wins, top_total), 'wins': top_wins, 'losses': (top_total-top_wins), 'total': top_total},
			'mid': {'percent': percent(mid_wins, mid_total), 'wins': mid_wins, 'losses': (mid_total-mid_wins), 'total': mid_total},
			'jun': {'percent': percent(jun_wins, jun_total), 'wins': jun_wins, 'losses': (jun_total-jun_wins), 'total': jun_total},
			'adc': {'percent': percent(adc_wins, adc_total), 'wins': adc_wins, 'losses': (adc_total-adc_wins), 'total': adc_total},
			'sup': {'percent': percent(sup_wins, sup_total), 'wins': sup_wins, 'losses': (sup_total-sup_wins), 'total': sup_total}}

	return JsonResponse(stats)

def duo(request):
	inHeaders = request.META

	p1 = Player.objects.filter(name=inHeaders['HTTP_P1'])[0]
	p2 = Player.objects.filter(name=inHeaders['HTTP_P2'])[0]

	total = 0
	wins = 0

	positions = ['top', 'mid', 'jun', 'adc', 'sup']

	for pos in positions:
		total += p1.flexmatch_set.filter(**{pos: p2.account_id}).count()
		wins += p1.flexmatch_set.filter(**{pos: p2.account_id}).filter(win=True).count()

	group = {'percent': percent(wins, total), 'wins': wins, 'losses': (total-wins), 'total': total}

	return JsonResponse(group)

def trio(request):
	inHeaders = request.META

	p1 = Player.objects.filter(name=inHeaders['HTTP_P1'])[0]
	p2 = Player.objects.filter(name=inHeaders['HTTP_P2'])[0]
	p3 = Player.objects.filter(name=inHeaders['HTTP_P3'])[0]

	total = 0
	wins = 0

	positions = ['top', 'mid', 'jun', 'adc', 'sup']

	for pos in positions:
		total_matches = p1.flexmatch_set.filter(**{pos: p2.account_id})
		wins_matches = p1.flexmatch_set.filter(**{pos: p2.account_id}).filter(win=True)

		for pos2 in positions:
			total += total_matches.filter(**{pos2: p3.account_id}).count()
			wins += wins_matches.filter(**{pos2: p3.account_id}).count()


	group = {'percent': percent(wins, total), 'wins': wins, 'losses': (total-wins), 'total': total}

	return JsonResponse(group)

def quad(request):
	inHeaders = request.META

	p1 = Player.objects.filter(name=inHeaders['HTTP_P1'])[0]
	p2 = Player.objects.filter(name=inHeaders['HTTP_P2'])[0]
	p3 = Player.objects.filter(name=inHeaders['HTTP_P3'])[0]
	p4 = Player.objects.filter(name=inHeaders['HTTP_P4'])[0]

	total = 0
	wins = 0

	positions = ['top', 'mid', 'jun', 'adc', 'sup']

	for pos in positions:
		total_matches = p1.flexmatch_set.filter(**{pos: p2.account_id})
		wins_matches = p1.flexmatch_set.filter(**{pos: p2.account_id}).filter(win=True)

		for pos2 in positions:
			total2_matches = total_matches.filter(**{pos2: p3.account_id})
			wins2_matches = wins_matches.filter(**{pos2: p3.account_id})

			for pos3 in positions:
				total += total2_matches.filter(**{pos3: p4.account_id}).count()
				wins += wins2_matches.filter(**{pos3: p4.account_id}).count()

	group = {'percent': percent(wins, total), 'wins': wins, 'losses': (total-wins), 'total': total}

	return JsonResponse(group)

def squad(request):
	inHeaders = request.META

	p1 = Player.objects.filter(name=inHeaders['HTTP_P1'])[0]
	p2 = Player.objects.filter(name=inHeaders['HTTP_P2'])[0]
	p3 = Player.objects.filter(name=inHeaders['HTTP_P3'])[0]
	p4 = Player.objects.filter(name=inHeaders['HTTP_P4'])[0]
	p5 = Player.objects.filter(name=inHeaders['HTTP_P5'])[0]

	total = 0
	wins = 0

	positions = ['top', 'mid', 'jun', 'adc', 'sup']

	for pos in positions:
		total_matches = p1.flexmatch_set.filter(**{pos: p2.account_id})
		wins_matches = p1.flexmatch_set.filter(**{pos: p2.account_id}).filter(win=True)

		for pos2 in positions:
			total2_matches = total_matches.filter(**{pos2: p3.account_id})
			wins2_matches = wins_matches.filter(**{pos2: p3.account_id})

			for pos3 in positions:
				total3_matches = total2_matches.filter(**{pos3: p4.account_id})
				wins3_matches = wins2_matches.filter(**{pos3: p4.account_id})

				for pos4 in positions:
					total += total3_matches.filter(**{pos4: p5.account_id}).count()
					wins += wins3_matches.filter(**{pos4: p5.account_id}).count()

	group = {'percent': percent(wins, total), 'wins': wins, 'losses': (total-wins), 'total': total}

	return JsonResponse(group)

#Populate Games from Riot API

def populate(request):
	inHeaders = request.META

	django_rq.enqueue(populate_background, inHeaders['HTTP_TEAM'])

	return JsonResponse({'Creating_Games': 'Exploding Poros'})

def solo_populate(request):
	inHeaders = request.META

	django_rq.enqueue(solo_populate_background, inHeaders['HTTP_NAME'])

	return JsonResponse({'Creating_Games': 'Exploding Poros'})

#Shared Methods

def headers():
	return { 'X-Riot-Token': os.environ.get('RIOT_KEY') }

def percent(portion, full):
	if full == 0:
		return 0
	return portion/full*100

#Background Tasks

def solo_populate_background(player_name):
	count = 0

	player = Player.objects.get(name = player_name)

	more_matches = True
	index = 0
	most_recent = player.solomatch_set.order_by('-timestamp')
	if len(most_recent) > 0:
		most_recent = most_recent[0].timestamp
	else:
		most_recent = 0

	while more_matches:
		r = requests.get(f"https://na1.api.riotgames.com/lol/match/v3/matchlists/by-account/{player.account_id}?queue=420&season=11&beginIndex={index}", headers=headers()).json()
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

				solo = SoloMatch(player = player,
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
				solo.save()

				count += 1
			else:
				more_matches = False
		index += 100
	return count

def populate_background(teamname):
	myteam = Team.objects.get(name = teamname)
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
	return count
