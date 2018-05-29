from django.shortcuts import render, get_object_or_404
from django.http import HttpResponse, JsonResponse
from teams.models import Team, Player
from django.core import serializers


def index(request):
    return HttpResponse('team index here')

	
def list(request):
	data = serializers.serialize("json", Team.objects.all())
	return JsonResponse(data, safe=False)