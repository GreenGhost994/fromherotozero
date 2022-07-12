from django.contrib import admin
from .models import League, Match, Player, PlayerSettings
# Register your models here.

admin.site.register(League)
admin.site.register(Match)
admin.site.register(Player)
admin.site.register(PlayerSettings)