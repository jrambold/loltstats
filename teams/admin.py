from django.contrib import admin

# Register your models here.
from .models import Team, Player, FlexMatch

admin.site.register(Team)
admin.site.register(Player)
admin.site.register(FlexMatch)