from django.urls import path

from . import views

urlpatterns = [
    path('', views.index, name='index'),
	path('list', views.list, name='list'),
	path('add_member', views.add_member, name='add_member'),
	path('populate', views.populate, name='populate'),
]