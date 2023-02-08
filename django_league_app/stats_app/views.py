from unicodedata import east_asian_width
from django.http import JsonResponse
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.db.models import Q

from league_app.models import League, Match, Player, PlayerSettings

from componenets.general import calculate_basic_stats, find_season
# Create your views here.

@login_required
def league_stats(request):
    try:
        league_value = PlayerSettings.objects.filter(user=request.user).values_list('league', flat=True)
        league_name = League.objects.get(pk=league_value[0])
    except:
        return redirect("leagueselect")
    # player_list = Player.objects.filter(accept=True).filter(league=league_value[0])
    match_list = Match.objects.filter(league=league_value[0])
    league_object = League.objects.get(pk=league_value[0])
    context = {}

    season = request.GET.get('season') or ''
    
    if season != '':
        date_filter = find_season(season)
        if 'month_filter' in date_filter:
            match_list = match_list.filter(created__year=date_filter['month_filter']['year'], created__month=date_filter['month_filter']['month'])
    
    context['season'] = season
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['matches'] = context['matches'].filter(user=self.request.user)
    #     # context['count'] = context['matches'].filter(complete=False).count()
        
    #     search_input = self.request.GET.get('search-area') or ''
    #     if search_input:
    #         context['matches'] = context['matches'].filter(title__icontains=search_input)
        
    #     context['search_input'] = search_input
        
    #     return context
    
    # if request.method == "POST":
    #     form = MatchForm(request.user, request.POST)
    #     if form.is_valid():
    #         mtch = form.save(commit=False)
    #         mtch.league = League.objects.get(pk=league_value)
    #         mtch.save()
    #         return redirect("matches")
    # else:
    #     form = MatchForm(request.user)

    context['league'] = league_name
    context['match_amount'] = len(match_list)
    context['players'], context['mvp'] = calculate_basic_stats(match_list, league_object)

    return render(request, 'stats_app/stats.html', {'context': context})


def player_stats(request, pk):
    try:
        league_value = PlayerSettings.objects.filter(user=request.user).values_list('league', flat=True)
        league_name = League.objects.get(pk=league_value[0])
    except:
        return redirect("leagueselect")

    season = request.GET.get('season') or ''
    match_list = Match.objects.filter(league=league_value[0]).filter(Q(atk1__id=pk) | Q(def1__id=pk) | Q(atk2__id=pk) | Q(def2__id=pk))

    if season != '':
        date_filter = find_season(season)
        if 'month_filter' in date_filter:
            match_list = match_list.filter(created__year=date_filter['month_filter']['year'], created__month=date_filter['month_filter']['month'])
    
    context = {}
    context['season'] = season
    players_data = Player.objects.filter(league=league_name).filter(accept=True)
    context['results'] = calc_player_stats(match_list, pk, players_data)

    return render(request, 'stats_app/player_stats.html', {'context': context})

from collections import defaultdict
def calc_player_stats(matches, player_id, players_data):
    def def_value():
        return 0

    def zero_div(x, y):
        if y: return x / y
        else: return 0

    results = {}

    atk_wins = 0
    def_wins = 0
    atk_defeats = 0
    def_defeats = 0

    domination_value = 2
    dominated_by = defaultdict(def_value)
    dominate = defaultdict(def_value)

    current_win_streak = 0
    current_defeat_streak = 0
    win_streak = 0
    defeat_streak = 0

    current_win_streak_atk = 0
    current_defeat_streak_atk = 0
    win_streak_atk = 0
    defeat_streak_atk = 0

    current_win_streak_def = 0
    current_defeat_streak_def = 0
    win_streak_def = 0
    defeat_streak_def = 0

    for m in matches:
        match_result = ''

        # wins/defeats
        # dominations
        # print('>>>', m.__dict__)
        if m.winner == '1':  # first team win
            if m.atk1_id == player_id:
                atk_wins += 1
                match_result = 'win_atk'

                dominate[m.atk2_id] += 1
                dominate[m.def2_id] += 1 
                dominated_by[m.atk2_id] = 0
                dominated_by[m.def2_id] = 0

            elif m.def1_id == player_id:
                def_wins += 1
                match_result = 'win_def'

                dominate[m.atk2_id] += 1
                dominate[m.def2_id] += 1 
                dominated_by[m.atk2_id] = 0
                dominated_by[m.def2_id] = 0

            elif m.atk2_id == player_id:
                atk_defeats += 1
                match_result = 'defeat_atk'

                dominate[m.atk1_id] = 0
                dominate[m.def1_id] = 0
                dominated_by[m.atk1_id] += 1 
                dominated_by[m.def1_id] += 1 

            elif m.def2_id == player_id:
                def_defeats += 1
                match_result = 'defeat_def'

                dominate[m.atk1_id] = 0
                dominate[m.def1_id] = 0
                dominated_by[m.atk1_id] += 1 
                dominated_by[m.def1_id] += 1 


        elif m.winner == '2':  # second team win
            if m.atk2_id == player_id:
                atk_wins += 1
                match_result = 'win_atk'

                dominate[m.atk1_id] += 1
                dominate[m.def1_id] += 1 
                dominated_by[m.atk1_id] = 0
                dominated_by[m.def1_id] = 0

            elif m.def2_id == player_id:
                def_wins += 1
                match_result = 'win_def'

                dominate[m.atk1_id] += 1
                dominate[m.def1_id] += 1 
                dominated_by[m.atk1_id] = 0
                dominated_by[m.def1_id] = 0

            elif m.atk1_id == player_id:
                atk_defeats += 1
                match_result = 'defeat_atk'

                dominate[m.atk2_id] = 0
                dominate[m.def2_id] = 0
                dominated_by[m.atk2_id] += 1 
                dominated_by[m.def2_id] += 1 

            elif m.def1_id == player_id:
                def_defeats += 1
                match_result = 'defeat_def'

                dominate[m.atk2_id] = 0
                dominate[m.def2_id] = 0
                dominated_by[m.atk2_id] += 1 
                dominated_by[m.def2_id] += 1 

        # streaks
        if match_result != '':
            if match_result == 'win_atk':
                current_win_streak += 1
                current_win_streak_atk += 1
                win_streak = max(win_streak, current_win_streak)
                win_streak_atk = max(win_streak_atk, current_win_streak_atk)
                current_defeat_streak = 0
                current_defeat_streak_atk = 0
                current_defeat_streak_def = 0

            elif match_result == 'win_def':
                current_win_streak += 1
                current_win_streak_def += 1
                win_streak = max(win_streak, current_win_streak)
                win_streak_def = max(win_streak_def, current_win_streak_def)
                current_defeat_streak = 0
                current_defeat_streak_atk = 0
                current_defeat_streak_def = 0

            elif match_result == 'defeat_atk':
                current_defeat_streak += 1
                current_defeat_streak_atk += 1
                defeat_streak = max(defeat_streak, current_defeat_streak)
                defeat_streak_atk = max(defeat_streak_atk, current_defeat_streak_atk)
                current_win_streak = 0
                current_win_streak_atk = 0
                current_win_streak_def = 0

            elif match_result == 'defeat_def':
                current_defeat_streak += 1
                current_defeat_streak_def += 1
                defeat_streak = max(defeat_streak, current_defeat_streak)
                defeat_streak_def = max(defeat_streak_def, current_defeat_streak_def)
                current_win_streak = 0
                current_win_streak_atk = 0
                current_win_streak_def = 0

    # dominations
    for k in list(dominate.keys()):
        if dominate[k] < domination_value:
            del dominate[k]
    for k in list(dominated_by.keys()):
        if dominated_by[k] < domination_value:
            del dominated_by[k]
    dominate.pop(player_id, None)
    dominated_by.pop(player_id, None)


    # get player info
    for i in players_data:
        if i.user.id == player_id:
            results['player_name'] = i.user
            break
    for k, v in dominate.items():
        for i in players_data:
            if k == i.user.id:
                dominate[k] = [i.user, dominate[k], '']
                break
    for k, v in dominated_by.items():
        for i in players_data:
            if k == i.user.id:
                dominated_by[k] = [i.user, dominated_by[k], '']
                break

    # get animation
    animation_dominate = {
        3: 'https://images.gr-assets.com/hostedimages/1407274294ra/10666949.gif',
        2: 'https://media1.giphy.com/media/KXLbV6qD0RfdvlD2Pi/giphy.gif?cid=ecf05e47u6tsuy1m8zyx3578wmos1ugq6bfyyp86ondp9nwr&rid=giphy.gif&ct=g',
        4: 'https://media1.giphy.com/media/yNFjQR6zKOGmk/giphy.gif?cid=790b7611e8f2b827de8ce00ddc2713c279cc485eb971d808&rid=giphy.gif&ct=g',
        6: 'https://media2.giphy.com/media/H2zV4rh9Zg2gFON8rw/giphy.gif?cid=790b7611c312d7b7808b8cef4591e65898163a34575a97d2&rid=giphy.gif&ct=g',
        7: 'https://media1.giphy.com/media/kfQeZEroEb7qohbFfE/giphy.gif?cid=ecf05e47ayvmf2iqzk0gg32y7z9r5ivks3g0hna9cbnsl2b0&rid=giphy.gif&ct=g',
        5: 'https://media3.giphy.com/media/26FfgonzyqqLWfjsA/giphy.gif?cid=ecf05e47w750fnap9ksb5wmmpr7k51vxqi5mibw267otxml7&rid=giphy.gif&ct=g',
        8: 'https://media0.giphy.com/media/RN96CaqhRoRHk4DlLV/giphy.gif?cid=ecf05e478qqi8t1a9oyj0kvu4z8xxm0mvgvnwaz7orgs5shz&rid=giphy.gif&ct=g',
        9: 'https://media2.giphy.com/media/3CIihjOfDNT0s/giphy.gif?cid=790b7611ed7fdfbbdee313a8e281d87c7de1bc9fe567f405&rid=giphy.gif&ct=g',
        10: 'https://media3.giphy.com/media/14RWYSvhLyzNm/giphy.gif?cid=ecf05e47z33qx2v8653t3i9fa1oagcdqoenuppny34r3agkj&rid=giphy.gif&ct=g',
        11: 'https://media3.giphy.com/media/fHoqSTQTsgSbfUoiTw/giphy.gif?cid=ecf05e47i1u3ok6illtz4dnf5g35amlkcjktk6q02eucycu6&rid=giphy.gif&ct=g',
        12: 'https://media0.giphy.com/media/XNQDgvHvDFnITnAAU5/200.gif?cid=ecf05e47v5nlcibm5p5ndvp9zvl6agwkt6tvq9bjxy8vr82n&rid=200.gif&ct=g',
        13: 'https://media3.giphy.com/media/1wPWMgD1Wrg9UwgBmo/200w.gif?cid=ecf05e475tt7kup7j150ch2z3973wxga6dw5e9x140ryv4yw&rid=200w.gif&ct=g',
    }
    animation_dominated_by = {
        2: 'https://media2.giphy.com/media/BY8ORoRpnJDXeBNwxg/giphy.gif?cid=ecf05e472sgwnrq43pd5agim3hfbqp744ok0pvnq1v808ifi&rid=giphy.gif&ct=g',
        3: 'https://i.pinimg.com/originals/80/4e/23/804e237839129b79dd956eb9c2ec1803.gif',
        4: 'https://64.media.tumblr.com/9c50498e29e3696460d3fd18849f89c6/d583c5658a278656-11/s400x600/90167665037c636237ba9ff42bc03383e087833a.gifv',
        5: 'https://c.tenor.com/Zi1l60KaBGMAAAAC/among-us-kill.gif',
        6: 'https://media3.giphy.com/media/YqE3jbSQQR6x9g19Kj/giphy.gif?cid=ecf05e47gk5f5aqbss1voxivdom2su7x9y6s0d3qek7tm7rh&rid=giphy.gif&ct=g',
        7: 'https://c.tenor.com/aRxE-vQoHDQAAAAC/jackson-hannah.gif',
        8: 'https://media4.giphy.com/media/l3q2K5jinAlChoCLS/giphy.gif?cid=790b76118abc6dae1cbaa17d16e7821dff07d9b7a4c58cad&rid=giphy.gif&ct=g',
        9: 'https://media3.giphy.com/media/efh1n8EkcQYEuTOGMn/giphy.gif?cid=790b76110a7cf2d6d5662cc9ce2caa59215f2684cfa15622&rid=giphy.gif&ct=g',
        10: 'https://media2.giphy.com/media/2BCnh0U8AsvBK/200.gif?cid=ecf05e47wg3ea8nxd7y4mhlqxmhr0e2rkrtxuvjq32ty43gx&rid=200.gif&ct=g',
        11: 'https://media3.giphy.com/media/5MZrg9tITn0Bi/200.gif?cid=ecf05e47i1u3ok6illtz4dnf5g35amlkcjktk6q02eucycu6&rid=200.gif&ct=g',
        12: 'https://media0.giphy.com/media/l0HUmvVJSs1ApEhry/200w.gif?cid=ecf05e47v05tnllt8fcb1dex6yjc7ed5vbqzbwtgo8fkzo9z&rid=200w.gif&ct=g',
        13: 'https://media2.giphy.com/media/kuJPDmkDIKPJp0eF6C/200w.gif?cid=ecf05e47cblqxta6qx82poy55nnbrpetrbjsa0xxafmjjtz0&rid=200w.gif&ct=g',
    }
    for k, v in dominate.items():
        if v[1] in animation_dominate:
            dominate[k][2] = animation_dominate[v[1]]

    for k, v in dominated_by.items():
        if v[1] in animation_dominated_by:
            dominated_by[k][2] = animation_dominated_by[v[1]]


    wins = atk_wins + def_wins
    defeats = atk_defeats + def_defeats
    games = wins + defeats

    results['games'] = games
    results['wins'] = {'general': wins, 'atk': atk_wins, 'def': def_wins}
    results['defeats'] = {'general': defeats, 'atk': atk_defeats, 'def': def_defeats}
    results['win_ratio'] = {'general': round(zero_div(wins,games), 2) * 100, 'atk': round(zero_div(atk_wins,(atk_wins+atk_defeats)), 2) * 100, 'def': round(zero_div(def_wins,(def_wins+def_defeats)), 2) * 100}
    results['streak'] = {'win': win_streak, 'win_atk': win_streak_atk, 'win_def': win_streak_def,
        'defeat': defeat_streak, 'defeat_atk': defeat_streak_atk, 'defeat_def': defeat_streak_def}
    results['dominate'] = dict(dominate)
    results['dominated_by'] = dict(dominated_by)

    print(results)
    return results



# from django.views.generic import TemplateView
# from chartjs.views.lines import BaseLineChartView
# class LineChartJSONView(BaseLineChartView):
#     def get_labels(self):
#         """Return 7 labels for the x-axis."""
#         return ["January", "February", "March", "April", "May", "June", "July"]

#     def get_providers(self):
#         """Return names of datasets."""
#         return ["Central", "Eastside", "Westside"]

#     def get_data(self):
#         """Return 3 datasets to plot."""

#         return [[75, 44, 92, 11, 44, 95, 35],
#                 [41, 92, 18, 3, 73, 87, 92],
#                 [87, 21, 94, 3, 90, 13, 65]]


# line_chart = TemplateView.as_view(template_name='line_chart.html')
# line_chart_json = LineChartJSONView.as_view()


# def get_data(request, *args, **kwargs):
#     data = {
#         "1": 1
#     }
#     return JsonResponse(data)