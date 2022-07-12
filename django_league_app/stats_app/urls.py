from django.urls import path
# from .views import LeagueDelete, LeagueDetail, LeagueList, LeagueCreate, LeagueUpdate, CustomLoginView, RegisterPage
# from .views import MatchList, MatchDetail, MatchList, MatchDelete
# from .views import PlayerCreate, PlayerDetail, PlayerList, PlayerDelete
# from .views import PlayerSettingsUpdate
# from .views import list_of_leagues, league_manage, confirm_request, league_select, create_match, update_match
from .views import league_stats, player_stats
# from .views import line_chart, line_chart_json, get_data
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('', league_stats, name='stats'),
    path('player/<int:pk>/', player_stats, name='playerstats'),
    # path('leagues', LeagueList.as_view(), name='leagues'),
    # path('chart', line_chart, name='line_chart'),
    # path(r'api/data/', get_data, name='api_data'),
    # path('chartJSON', line_chart_json, name='line_chart_json'),
]
