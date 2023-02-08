from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic.list import ListView
from django.views.generic.detail import DetailView
from django.views.generic.edit import CreateView, UpdateView, DeleteView, FormView
from django.urls import reverse_lazy, reverse
from django.http import HttpResponseRedirect

from django.utils.decorators import method_decorator

from django.contrib.auth.views import LoginView, PasswordChangeView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm, UserChangeForm
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from django.core.exceptions import ValidationError

from .forms import SettingsForm, MatchForm

from .models import League, Match, Player, PlayerSettings, User

from componenets.general import match_proposal


# Create your views here.

# def add_match(request):
#     return HttpResponse('Add match')


from django.core.exceptions import PermissionDenied
from functools import wraps

def requires_league_membership(view):
    @wraps(view)
    def _view(request, *args, **kwargs):
        if not Player.objects.filter(user=request.user.id).filter(accept=True).filter(league=kwargs['pk']).exists():
            if not League.objects.filter(user=request.user.id).filter(id=kwargs['pk']).exists():
                raise PermissionDenied
        return view(request, *args, **kwargs)
    return _view

def requires_league_membership_request(view):
    @wraps(view)
    def _view(request, *args, **kwargs):
        player = Player.objects.filter(id=kwargs['pk']).get()
        if not Player.objects.filter(league=player.league).filter(user=request.user.id).exists():
            if not League.objects.filter(user=request.user.id).filter(id=player.league.id).exists():
                raise PermissionDenied
        return view(request, *args, **kwargs)
    return _view

def requires_league_membership_match(view):
    @wraps(view)
    def _view(request, *args, **kwargs):
        match = Match.objects.filter(id=kwargs['pk']).get()
        if not Player.objects.filter(league=match.league).filter(user=request.user.id).exists():
            raise PermissionDenied
        return view(request, *args, **kwargs)
    return _view


class PasswordsChangeView(LoginRequiredMixin, PasswordChangeView):
    template_name = 'league_app/password.html'
    form_class = PasswordChangeForm
    success_url = reverse_lazy('main')

class CustomLoginView(LoginView):
    template_name = 'league_app/login.html'
    fileds =  '__all__'
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse_lazy('matchcreate')

class RegisterPage(FormView):
    template_name = 'league_app/register.html'
    form_class = UserCreationForm
    redirect_authenticated_user = True
    success_url = reverse_lazy('matchcreate')

    def form_valid(self, form):
        user = form.save()
        if user is not None:
            login(self.request, user)
        return super(RegisterPage, self).form_valid(form)

    def get(self, *args, **kwarges):
        if self.request.user.is_authenticated:
            return redirect('matchcreate')
        return super(RegisterPage, self).get(*args, **kwarges)
    

# LEAGUE
class LeagueList(LoginRequiredMixin, ListView):
    model = League
    context_object_name = 'leagues'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['leagues'] = context['leagues'].filter(user=self.request.user)
        # context['count'] = context['leagues'].filter(complete=False).count()
        
        search_input = self.request.GET.get('search-area') or ''
        if search_input:
            context['leagues'] = context['leagues'].filter(title__icontains=search_input)
        
        context['search_input'] = search_input
        
        return context

@method_decorator(requires_league_membership, name='dispatch')
class LeagueDetail(LoginRequiredMixin, DetailView):
    model = League
    context_object_name = 'league'
    template_name = 'league_app/league.html'

class LeagueCreate(LoginRequiredMixin, CreateView):
    model = League
    fields = ['title', 'description', 'team1', 'team2',
    'mvp_total', 'mvp_atk_def', 'mvp_hybrid', 'mvp_hybrid_rel_tol', 'mvp_hybrid_abs_tol']
    success_url = reverse_lazy('league_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        return super(LeagueCreate, self).form_valid(form)


@method_decorator(requires_league_membership, name='dispatch')
class LeagueUpdate(LoginRequiredMixin, UpdateView):
    model = League
    fields = ['description', 'team1', 'team2',
    'mvp_total', 'mvp_atk_def', 'mvp_hybrid', 'mvp_hybrid_rel_tol', 'mvp_hybrid_abs_tol']
    success_url = reverse_lazy('league_list')


@method_decorator(requires_league_membership, name='dispatch')
class LeagueDelete(LoginRequiredMixin, DeleteView):
    model = League
    context_object_name = 'league'
    success_url = reverse_lazy('league_list')    


# MATCH
class MatchList(LoginRequiredMixin, ListView):
    model = Match
    context_object_name = 'matches'
    paginate_by = 10

    def get_queryset(self):
        try:
            id_tuple = PlayerSettings.objects.filter(user=self.request.user).values_list('league', flat=True)[0]
        except:
            return Match.objects.none()
        # form.instance.league = League.objects.filter(id__in=id_tuple)[0]
        queryset = Match.objects.filter(league_id=id_tuple).order_by('-created')

        return queryset
    # def get_context_data(self, **kwargs):
    #     context = super().get_context_data(**kwargs)
    #     context['matches'] = context['matches'].filter(user=self.request.user)
    #     # context['count'] = context['matches'].filter(complete=False).count()
        
    #     search_input = self.request.GET.get('search-area') or ''
    #     if search_input:
    #         context['matches'] = context['matches'].filter(title__icontains=search_input)
        
    #     context['search_input'] = search_input
        
    #     return context

@login_required
def create_match(request):
    try:
        league_value = PlayerSettings.objects.filter(user=request.user).values_list('league', flat=True)[0]
    except:
        return redirect("leagueselect")
    if request.method == "POST":
        form = MatchForm(request.user, request.POST)
        if form.is_valid():
            mtch = form.save(commit=False)
            mtch.league = League.objects.get(pk=league_value)
            mtch.save()
            return redirect("matches")
    else:
        form = MatchForm(request.user)

    context = {'form': form}
    return render(request, 'league_app/match_form.html', {'context': context})

@login_required
@requires_league_membership_match
def update_match(request, pk):
    try:
        league_value = PlayerSettings.objects.filter(user=request.user).values_list('league', flat=True)[0]
    except:
        return redirect("leagueselect")
    match = Match.objects.get(id=pk)

    if request.method == "POST":
        form = MatchForm(request.user, request.POST, instance=match)
        if form.is_valid():
            mtch = form.save(commit=False)
            mtch.league = League.objects.get(pk=league_value)
            mtch.save()
            return redirect("matches")
    else:
        form = MatchForm(request.user, instance=match)

    # form = MatchForm(request.user, instance=match)
    context = {'form': form}
    return render(request, 'league_app/match_form.html', {'context': context})

@method_decorator(requires_league_membership_match, name='dispatch')
class MatchDetail(LoginRequiredMixin, DetailView):
    model = Match
    context_object_name = 'match'
    template_name = 'league_app/match.html'

# class MatchCreate(LoginRequiredMixin, CreateView):
#     model = Match
#     fields = ['atk1', 'def1', 'atk2', 'def2', 'score',  'atk1',  'winner']
#     success_url = reverse_lazy('matches')

#     def form_valid(self, form):
#         form.instance.user = self.request.user
#         id_tuple = PlayerSettings.objects.filter(user=self.request.user).values_list('league', flat=True)
#         form.instance.league = League.objects.filter(id__in=id_tuple)[0]
#         return super(MatchCreate, self).form_valid(form)

    
# class MatchUpdate(LoginRequiredMixin, UpdateView):
#     model = Match
#     fields = ['atk1', 'def1', 'atk2', 'def2', 'score',  'atk1',  'winner']
#     success_url = reverse_lazy('matches')

@method_decorator(requires_league_membership_match, name='dispatch')
class MatchDelete(LoginRequiredMixin, DeleteView):
    model = Match
    context_object_name = 'match'
    success_url = reverse_lazy('matches')


# PLAYER
class PlayerList(LoginRequiredMixin, ListView):
    model = Player
    context_object_name = 'players'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['players'] = context['players'].filter(user=self.request.user)
        context['players'] = context['players'].filter(accept=False)
        
        return context

class PlayerDetail(LoginRequiredMixin, DetailView):
    model = Player
    context_object_name = 'player'
    template_name = 'league_app/player.html'

class PlayerCreate(LoginRequiredMixin, CreateView):
    model = Player
    fields = ['league']
    success_url = reverse_lazy('league_list')

    def form_valid(self, form):
        form.instance.user = self.request.user
        # for i in Player.objects.filter(user=self.request.user):
        #     if i.league == form.instance.league:
        #         raise ValidationError(f"You have forgotten about Fred!")
        return super(PlayerCreate, self).form_valid(form)


# class PlayerUpdate(LoginRequiredMixin, UpdateView):
#     model = Player
#     fields = '__all__'
#     success_url = reverse_lazy('players')

class PlayerDelete(LoginRequiredMixin, DeleteView):
    model = Player
    context_object_name = 'player'
    success_url = reverse_lazy('league_list')


# OTHER
@login_required
def list_of_leagues(request):
    leagues = League.objects.filter(user=request.user)
    players = Player.objects.filter(user=request.user).filter(accept=True)

    return render(request, 'league_app/list_of_leagues.html', {'leagues': leagues, 'players': players})

@login_required
@requires_league_membership
def league_manage(request, pk):
    league_data = League.objects.filter(id=pk)[0]
    players_data = Player.objects.filter(league=pk)

    return render(request, 'league_app/league_manage.html', {'league': league_data, 'players': players_data})

@login_required
@requires_league_membership_request
def confirm_request(request, pk):
    player_data = Player.objects.get(id=pk)
    player_data.accept = True
    player_data.save()

    return HttpResponseRedirect(reverse('leaguemanage', args=[player_data.league.id]))

@login_required
def league_select(request):
    # player_settings = PlayerSettings.objects
    context ={}
    try:    
        initial_value = PlayerSettings.objects.filter(user=request.user).values_list('league', flat=True)[0]
        initial_data = {"league": initial_value}
    except:
        initial_data = None
    if request.method == 'POST':
        context['form'] = SettingsForm(request.user, request.POST, initial_data)
        if context['form'].is_valid():
            # context['form'].save() 
            PlayerSettings.objects.update_or_create(
            user=request.user,
            defaults={'league': League.objects.get(pk=context['form'].data['league'])}
            )

    else:
        context['form'] = SettingsForm(request.user, initial_data)

    # form.fields["league"].queryset = Player.objects.filter(user=request.user).filter(accept=True)
    return render(request, 'league_app/league_select.html', {'context': context})


@login_required
def player_positions(request):
    try:
        league_value = PlayerSettings.objects.filter(user=request.user).values_list('league', flat=True)[0]
    except:
        return redirect("leagueselect")
    results = {}
    players_input = {}

    players_data = Player.objects.filter(league=league_value).filter(accept=True)

    search_input = request.GET.get('p1') or ''
    if search_input:
        p1 = int(request.GET['p1'])
        p2 = int(request.GET['p2'])
        p3 = int(request.GET['p3'])
        p4 = int(request.GET['p4'])
        s1 = request.GET['s1']
        s2 = request.GET['s2']
        s3 = request.GET['s3']
        s4 = request.GET['s4']
        players_input = {'p1': p1, 'p2': p2, 'p3': p3, 'p4': p4,
        's1': s1, 's2': s2, 's3': s3, 's4': s4}

        print([p1, p2, p3, p4], set([p1, p2, p3, p4]))
        if len([p1, p2, p3, p4]) != len(set([p1, p2, p3, p4])):
            return render(request, 'league_app/player_positions.html', {'results': {}, 'players': players_data, 'previous': players_input})
        match_list = Match.objects.filter(league=league_value)

        results=match_proposal(match_list, players_input, players_data)
        # results=match_list
        # league_object = League.objects.get(pk=league_value[0])

    # league_data = League.objects.filter(id=league_value)[0]


    
    # print(league_value)
    # print(players_data[0].__dict__)

    return render(request, 'league_app/player_positions.html', {'results': results, 'players': players_data, 'previous': players_input})




# def league_selected(request, id_user, id_league):
#     PlayerSettings.objects.update_or_create(
#     user=id_user,
#     defaults={'league': id_league}
#     )

#     return HttpResponseRedirect(reverse('leaguelist', args=[player_data.league.id]))




# class PlayerSettingsUpdate(LoginRequiredMixin, UpdateView):
#     model = PlayerSettings
#     fields = '__all__'
#     success_url = reverse_lazy('league_list')