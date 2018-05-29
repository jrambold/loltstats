from django.shortcuts import render
from django.http import HttpResponse, JsonResponse
from teams.models import Team, Player
from . import serializers


def index(request):
    return JsonResponse(TeamSerializer, safe=False)