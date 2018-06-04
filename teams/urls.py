from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
	path('list', views.list, name='list'),
	path('get_team_members', views.get_team_members, name='get_team_members'),
	path('add_member', views.add_member, name='add_member'),
	path('populate', views.populate, name='populate'),
	path('best_by_position', views.best_by_position, name='best_by_position'),
	path('custom_team', views.custom_team, name='custom_team'),
	path('duo', views.duo, name='duo'),
	path('trio', views.trio, name='trio'),
	path('quad', views.quad, name='quad'),
	path('squad', views.squad, name='squad'),
	path('solo_populate', views.solo_populate, name='solo_populate'),
	path('solo_stats', views.solo_stats, name='solo_stats'),
]
