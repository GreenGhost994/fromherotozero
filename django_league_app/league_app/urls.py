from django.urls import path
from .views import LeagueDelete, LeagueDetail, LeagueList, LeagueCreate, LeagueUpdate, CustomLoginView, RegisterPage
from .views import MatchList, MatchDetail, MatchList, MatchDelete
from .views import PlayerCreate, PlayerDetail, PlayerList, PlayerDelete
# from .views import PlayerSettingsUpdate
from .views import list_of_leagues, league_manage, confirm_request, league_select, create_match, update_match, player_positions
from django.contrib.auth.views import LogoutView



urlpatterns = [
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(next_page='login'), name='logout'),
    path('register/', RegisterPage.as_view(), name='register'),
    
    # path('', LeagueList.as_view(), name='league_list'),
    path('', create_match, name='main'),
    
    path('leaguelist', list_of_leagues, name='league_list'),
    path('leagues', LeagueList.as_view(), name='leagues'),
    path('league/<int:pk>/', LeagueDetail.as_view(), name='league'),
    path('leaguecreate/', LeagueCreate.as_view(), name='leaguecreate'),
    path('leagueupdate/<int:pk>/', LeagueUpdate.as_view(), name='leagueupdate'),
    path('leaguedelete/<int:pk>/', LeagueDelete.as_view(), name='leaguedelete'),

    path('leaguemanage/<int:pk>/', league_manage, name='leaguemanage'),

    path('matches/', MatchList.as_view(), name='matches'),
    path('match/<int:pk>/', MatchDetail.as_view(), name='match'),
    # path('matchcreate/', MatchCreate.as_view(), name='matchcreate'),
    path('matchcreate/', create_match, name='matchcreate'),
    # path('matchupdate/<int:pk>/', MatchUpdate.as_view(), name='matchupdate'),
    path('matchupdate/<int:pk>/', update_match, name='matchupdate'),
    path('matchdelete/<int:pk>/', MatchDelete.as_view(), name='matchdelete'),

    path('playerrequests/', PlayerList.as_view(), name='playerrequests'),
    path('player/<int:pk>/', PlayerDetail.as_view(), name='player'),
    path('playercreate/', PlayerCreate.as_view(), name='playercreate'),
    path('requestdelete/<int:pk>/', PlayerDelete.as_view(), name='requestdelete'),
    path('requestaccept/<int:pk>/', confirm_request, name='requestaccept'),

    path('leagueselect/', league_select, name='leagueselect'),

    path('matchassistant/', player_positions, name='matchassistant'),
    # path('leagueselect/<int:id_league>/', league_select, name='leagueselected'),
]