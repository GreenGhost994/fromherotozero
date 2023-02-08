from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
# Create your models here.

# class Match(models.Model):
#     player_atk_1 = 
#     player_def_1 = 
#     player_atk_2 = 
#     player_def_2 = 
#     winner = 
#     result = 
#     created = models.DateTimeField(auto_now_add=True)

#     def __str__(self):
#         return f({self.winner}

class League(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    title = models.CharField(max_length=200)
    description = models.TextField(null=True, blank=True)
    team1 = models.CharField(max_length=200, null=False, blank=False, verbose_name='First team name')
    team2 = models.CharField(max_length=200, null=False, blank=False, verbose_name='Second team name')
    created = models.DateTimeField(auto_now_add=True)

    mvp_total = models.IntegerField(null=False, blank=False, verbose_name='Min games for Total MVP')
    mvp_atk_def = models.IntegerField(null=False, blank=False, verbose_name='Min games for Attack and Defense MVP')
    mvp_hybrid = models.IntegerField(null=False, blank=False, verbose_name='Min games for Hybrid MVP')
    mvp_hybrid_rel_tol = models.FloatField(null=False, blank=False, verbose_name='Hybrid MVP relative tolerance')
    mvp_hybrid_abs_tol = models.IntegerField(null=False, blank=False, verbose_name='Hybrid MVP absolute tolerance')

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['created']


class Match(models.Model):
        
    SCORE_CHOICE = (
            ('9', '10:9'),
            ('8', '10:8'),
            ('7', '10:7'),
            ('6', '10:6'),
            ('5', '10:5'),
            ('4', '10:4'),
            ('3', '10:3'),
            ('2', '10:2'),
            ('1', '10:1'),
            ('0', '10:0'),
        )

    WINNER_CHOICE = (
            ('1', 'TEAM 1'),
            ('2', 'TEAM 2'),
        )

    league = models.ForeignKey(League, on_delete=models.PROTECT, null=False, blank=False)
    atk1 = models.ForeignKey(User, on_delete=models.PROTECT, null=False, blank=False, related_name="atk1", verbose_name='atk1')
    def1 = models.ForeignKey(User, on_delete=models.PROTECT, null=False, blank=False, related_name="def1", verbose_name='def1')
    atk2 = models.ForeignKey(User, on_delete=models.PROTECT, null=False, blank=False, related_name="atk2", verbose_name='atk2')
    def2 = models.ForeignKey(User, on_delete=models.PROTECT, null=False, blank=False, related_name="def2", verbose_name='def2')
    score = models.CharField(max_length=1, choices=SCORE_CHOICE)
    winner = models.CharField(max_length=1, choices=WINNER_CHOICE)
    # created = models.DateTimeField(auto_now_add=True)
    created = models.DateTimeField(default=timezone.now)



    def __str__(self):
        if self.winner == '1':
            return f'{self.atk1} + {self.def1} vs {self.atk2} + {self.def2} (10:{self.score})'
        else:
            return f'{self.atk1} + {self.def1} vs {self.atk2} + {self.def2} ({self.score}:10)'

    class Meta:
        ordering = ['created']


class Player(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True)
    league = models.ForeignKey(League, on_delete=models.CASCADE, null=True, blank=True)
    accept = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.league}'

    class Meta:
        ordering = ['league']
        unique_together = ["user", "league"]


class PlayerSettings(models.Model):
    # user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, unique=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE, null=True, blank=True, related_name='user')
    league = models.ForeignKey(League, on_delete=models.CASCADE, null=True, blank=True, verbose_name="Current league")
    # league = Player.objects.filter(accept=True)
    # league = Player.objects.filter(accept=True)

    def __str__(self):
        return f'Player {self.user} - {self.league} league'

    class Meta:
        ordering = ['user']