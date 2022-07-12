from django import forms

from .models import PlayerSettings, Player, League, Match, User

class SettingsForm(forms.ModelForm):
    class Meta:
        model = PlayerSettings
        fields = ['league']

    def __init__(self, user, *args, **kwargs):
        super(SettingsForm, self).__init__(*args, **kwargs)
        # self.fields['league'].queryset = Player.objects.filter(user=user).filter(accept=True)
        id_tuple = Player.objects.filter(user=user).filter(accept=True).values_list('league', flat=True)
        self.fields['league'].queryset = League.objects.filter(id__in=id_tuple)

  
class MatchForm(forms.ModelForm):
    def clean(self):
        cleaned_data = super().clean()
        atk1 = cleaned_data.get("atk1")
        def1 = cleaned_data.get("def1")
        atk2 = cleaned_data.get("atk2")
        def2 = cleaned_data.get("def2")
        x = [atk1, def1, atk2, def2]
        if len(x) > len(set(x)):
            raise forms.ValidationError("Error: Duplicated player")

    class Meta:
        model = Match
        fields = ['atk1', 'def1', 'atk2', 'def2', 'score',  'atk1',  'winner']

    def __init__(self, user, *args, **kwargs):
        super(MatchForm, self).__init__(*args, **kwargs)

        # team names
        current_league = PlayerSettings.objects.filter(user=user).values_list('league', flat=True)[0]
        current_league_model =  League.objects.get(pk=current_league)
        team1_name =  current_league_model.team1
        team2_name =  current_league_model.team2

        self.fields['winner'].choices = (
            (1, team1_name),
            (2, team2_name),
        )

        self.fields['atk1'].label = f'[{team1_name}] Attack'
        self.fields['def1'].label = f'[{team1_name}] Defense'
        self.fields['atk2'].label = f'[{team2_name}] Attack'
        self.fields['def2'].label = f'[{team2_name}] Defense'

        # player filter
        id_tuple = PlayerSettings.objects.filter(user=user).values_list('league', flat=True)
        id_tuple_user = Player.objects.filter(league__in=id_tuple).filter(accept=True).values_list('user', flat=True)
        list_of_players = User.objects.filter(id__in=id_tuple_user)
        self.fields['atk1'].queryset = list_of_players
        self.fields['def1'].queryset = list_of_players
        self.fields['atk2'].queryset = list_of_players
        self.fields['def2'].queryset = list_of_players

# class MatchUpdateForm(forms.ModelForm):
#     def clean(self):
#         cleaned_data = super().clean()
#         atk1 = cleaned_data.get("atk1")
#         def1 = cleaned_data.get("def1")
#         atk2 = cleaned_data.get("atk2")
#         def2 = cleaned_data.get("def2")
#         x = [atk1, def1, atk2, def2]
#         if len(x) > len(set(x)):
#             raise forms.ValidationError("Error: Duplicated player")

#     class Meta:
#         model = Match
#         fields = ['atk1', 'def1', 'atk2', 'def2', 'score',  'atk1',  'winner']

#     def __init__(self, user, *args, **kwargs):
#         super(MatchForm, self).__init__(*args, **kwargs)

#         # team names
#         current_league = PlayerSettings.objects.filter(user=user).values_list('league', flat=True)[0]
#         current_league_model =  League.objects.get(pk=current_league)
#         team1_name =  current_league_model.team1
#         team2_name =  current_league_model.team2

#         self.fields['winner'].choices = (
#             (1, team1_name),
#             (2, team2_name),
#         )

#         self.fields['atk1'].label = f'[{team1_name}] Attack'
#         self.fields['def1'].label = f'[{team1_name}] Defense'
#         self.fields['atk2'].label = f'[{team2_name}] Attack'
#         self.fields['def2'].label = f'[{team2_name}] Defense'

#         # player filter
#         id_tuple = PlayerSettings.objects.filter(user=user).values_list('league', flat=True)
#         id_tuple_user = Player.objects.filter(league__in=id_tuple).filter(accept=True).values_list('user', flat=True)
#         list_of_players = User.objects.filter(id__in=id_tuple_user)
#         self.fields['atk1'].queryset = list_of_players
#         self.fields['def1'].queryset = list_of_players
#         self.fields['atk2'].queryset = list_of_players
#         self.fields['def2'].queryset = list_of_players
