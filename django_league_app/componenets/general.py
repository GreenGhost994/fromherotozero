from collections import defaultdict
from math import isclose
def calculate_basic_stats(match_list, mvp_limits):
    def def_value():
        return {'wins': 0, 'losses': 0, 'win_ratio': 0,
                'atk_wins': 0, 'atk_losses': 0, 'atk_win_ratio': 0,
                'def_wins': 0, 'def_losses': 0, 'def_win_ratio': 0,
                'games': 0, 'atk_games': 0, 'def_games': 0,
                '109': 0, '108': 0, '107': 0, '106': 0, '105': 0,
                '104': 0, '103': 0, '102': 0, '101': 0, '100': 0,
                '010': 0, '110': 0, '210': 0, '310': 0, '410': 0,
                '510': 0, '610': 0, '710': 0, '810': 0, '910': 0
                }

    def zero_div(x, y):
        if y: return x / y
        else: return 0

    def clean_low(x):
        if x < 10:
            x = ''
        else:
            x = str(x)+'%'
        return x

    results = defaultdict(def_value)
    for mtch in match_list:
        results[mtch.atk1]['games'] += 1
        results[mtch.atk1]['atk_games'] += 1
        results[mtch.def1]['games'] += 1
        results[mtch.def1]['def_games'] += 1
        results[mtch.atk2]['games'] += 1
        results[mtch.atk2]['atk_games'] += 1
        results[mtch.def2]['games'] += 1
        results[mtch.def2]['def_games'] += 1

        if int(mtch.winner) == 1:  # first team win
            results[mtch.atk1]['wins'] += 1
            results[mtch.atk1]['atk_wins'] += 1
            results[mtch.def1]['wins'] += 1
            results[mtch.def1]['def_wins'] += 1
            results[mtch.atk2]['losses'] += 1
            results[mtch.atk2]['def_losses'] += 1
            results[mtch.def2]['losses'] += 1
            results[mtch.def2]['def_losses'] += 1

            results[mtch.atk1][mtch.get_score_display().replace(':', '')] += 1
            results[mtch.def1][mtch.get_score_display().replace(':', '')] += 1
            results[mtch.atk2][reverse_score(mtch.get_score_display()).replace(':', '')] += 1
            results[mtch.def2][reverse_score(mtch.get_score_display()).replace(':', '')] += 1

        else:  # second team win
            results[mtch.atk2]['wins'] += 1
            results[mtch.atk2]['atk_wins'] += 1
            results[mtch.def2]['wins'] += 1
            results[mtch.def2]['def_wins'] += 1
            results[mtch.atk1]['losses'] += 1
            results[mtch.atk1]['atk_losses'] += 1
            results[mtch.def1]['losses'] += 1
            results[mtch.def1]['def_losses'] += 1

            results[mtch.atk2][mtch.get_score_display().replace(':', '')] += 1
            results[mtch.def2][mtch.get_score_display().replace(':', '')] += 1
            results[mtch.atk1][reverse_score(mtch.get_score_display()).replace(':', '')] += 1
            results[mtch.def1][reverse_score(mtch.get_score_display()).replace(':', '')] += 1


    for k, v in results.items():
        win_ratio = round(zero_div(v['wins'], (v['wins']+v['losses'])), 2)
        v['win_ratio'] = [win_ratio, clean_low(int(win_ratio * 100))]
        atk_win_ratio = round(zero_div(v['atk_wins'], (v['atk_wins']+v['atk_losses'])), 2)
        v['atk_win_ratio'] = [atk_win_ratio, clean_low(int(atk_win_ratio * 100))]
        def_win_ratio = round(zero_div(v['def_wins'], (v['def_wins']+v['def_losses'])), 2)
        v['def_win_ratio'] = [def_win_ratio, clean_low(int(def_win_ratio * 100))]


    # MVP stats
    mvp ={'total': {'user': '', 'ratio': 0},
        'atk': {'user': '', 'ratio': 0},
        'def': {'user': '', 'ratio': 0},
        'hybrid': {'user': '', 'ratio': 0},
    }

    for k, v in results.items():
        if v['games'] >= mvp_limits.mvp_total:
            if v['win_ratio'][0] > mvp['total']['ratio']:
                mvp['total']['ratio'] = v['win_ratio'][0]
                mvp['total']['user'] = k
        if v['atk_games'] >= mvp_limits.mvp_atk_def:
            if v['atk_win_ratio'][0] > mvp['atk']['ratio']:
                mvp['atk']['ratio'] = v['atk_win_ratio'][0]
                mvp['atk']['user'] = k
        if v['def_games'] >= mvp_limits.mvp_atk_def:
            if v['def_win_ratio'][0] > mvp['def']['ratio']:
                mvp['def']['ratio'] = v['def_win_ratio'][0]
                mvp['def']['user'] = k
        if v['games'] >= mvp_limits.mvp_hybrid:   
            if isclose(v['atk_games'], v['def_games'],
                rel_tol=mvp_limits.mvp_hybrid_rel_tol, abs_tol=mvp_limits.mvp_hybrid_abs_tol):
                if v['win_ratio'][0] > mvp['hybrid']['ratio']:
                    mvp['hybrid']['ratio'] = v['win_ratio'][0]
                    mvp['hybrid']['user'] = k
                    print('tak', k)

    # print(dict(results))
    return dict(results), mvp

def find_season(text):
    text = text.replace(" ", "")
    if "/" in text:
        date = text.split("/")
        month = date[0].zfill(2)
        year = date[1]
        return {'month_filter': {'year': year, 'month': month}}

def reverse_score(score):
    score = score.split(':')
    score = f'{score[1]}:{score[0]}'
    return score

def match_proposal(matches, players, players_data):
    def check_same_contents(nums1, nums2):
        for x in set(nums1 + nums2):
            if nums1.count(x) != nums2.count(x):
                return False
        return True
    
    def def_chosen_matches():
        return []

    played_matches = {}
    player_dict = {players['p1']: players['s1'],
        players['p2']: players['s2'],
        players['p3']: players['s3'],
        players['p4']: players['s4']}

    played_matches = {
        (players['p1'], players['p2'], players['p3'], players['p4']): 0,
        (players['p2'], players['p3'], players['p4'], players['p1']): 0,
        (players['p3'], players['p4'], players['p1'], players['p2']): 0,
        (players['p4'], players['p1'], players['p2'], players['p3']): 0,
        (players['p4'], players['p3'], players['p2'], players['p1']): 0,
        (players['p3'], players['p2'], players['p1'], players['p4']): 0,
        (players['p2'], players['p1'], players['p4'], players['p3']): 0,
        (players['p1'], players['p4'], players['p3'], players['p2']): 0,
        
        (players['p1'], players['p2'], players['p4'], players['p3']): 0,
        (players['p2'], players['p3'], players['p1'], players['p4']): 0,
        (players['p3'], players['p4'], players['p2'], players['p1']): 0,
        (players['p4'], players['p1'], players['p3'], players['p2']): 0,
        (players['p4'], players['p3'], players['p1'], players['p2']): 0,
        (players['p3'], players['p2'], players['p4'], players['p1']): 0,
        (players['p2'], players['p1'], players['p3'], players['p4']): 0,
        (players['p1'], players['p4'], players['p2'], players['p3']): 0,
        
        (players['p1'], players['p3'], players['p2'], players['p4']): 0,
        (players['p2'], players['p4'], players['p3'], players['p1']): 0,
        (players['p3'], players['p1'], players['p4'], players['p2']): 0,
        (players['p4'], players['p2'], players['p1'], players['p3']): 0,
        (players['p4'], players['p2'], players['p3'], players['p1']): 0,
        (players['p3'], players['p1'], players['p2'], players['p4']): 0,
        (players['p2'], players['p4'], players['p1'], players['p3']): 0,
        (players['p1'], players['p3'], players['p4'], players['p2']): 0,
    }

    # filter matches
    for match in matches:
        if check_same_contents(list(player_dict.keys()), [match.atk1.id, match.def1.id, match.atk2.id, match.def2.id]):
            played_matches[(match.atk1.id, match.def1.id, match.atk2.id, match.def2.id)] += 1

    # merge similar matches
    reduced_played_matches =  {
        (players['p1'], players['p2'], players['p3'], players['p4']): [played_matches[(players['p1'], players['p2'], players['p3'], players['p4'])] + played_matches[(players['p3'], players['p4'], players['p1'], players['p2'])], 0, ''],
        (players['p2'], players['p3'], players['p4'], players['p1']): [played_matches[(players['p2'], players['p3'], players['p4'], players['p1'])] + played_matches[(players['p4'], players['p1'], players['p2'], players['p3'])], 0, ''],
        (players['p4'], players['p3'], players['p2'], players['p1']): [played_matches[(players['p4'], players['p3'], players['p2'], players['p1'])] + played_matches[(players['p2'], players['p1'], players['p4'], players['p3'])], 0, ''], 
        (players['p3'], players['p2'], players['p1'], players['p4']): [played_matches[(players['p3'], players['p2'], players['p1'], players['p4'])] + played_matches[(players['p1'], players['p4'], players['p3'], players['p2'])], 0, ''],
        (players['p1'], players['p2'], players['p4'], players['p3']): [played_matches[(players['p1'], players['p2'], players['p4'], players['p3'])] + played_matches[(players['p4'], players['p3'], players['p1'], players['p2'])], 0, ''],
        (players['p2'], players['p3'], players['p1'], players['p4']): [played_matches[(players['p2'], players['p3'], players['p1'], players['p4'])] + played_matches[(players['p1'], players['p4'], players['p2'], players['p3'])], 0, ''],   
        (players['p3'], players['p4'], players['p2'], players['p1']): [played_matches[(players['p3'], players['p4'], players['p2'], players['p1'])] + played_matches[(players['p2'], players['p1'], players['p3'], players['p4'])], 0, ''],    
        (players['p4'], players['p1'], players['p3'], players['p2']): [played_matches[(players['p4'], players['p1'], players['p3'], players['p2'])] + played_matches[(players['p3'], players['p2'], players['p4'], players['p1'])], 0, ''],
        (players['p1'], players['p3'], players['p2'], players['p4']): [played_matches[(players['p1'], players['p3'], players['p2'], players['p4'])] + played_matches[(players['p2'], players['p4'], players['p1'], players['p3'])], 0, ''],    
        (players['p2'], players['p4'], players['p3'], players['p1']): [played_matches[(players['p2'], players['p4'], players['p3'], players['p1'])] + played_matches[(players['p3'], players['p1'], players['p2'], players['p4'])], 0, ''],   
        (players['p3'], players['p1'], players['p4'], players['p2']): [played_matches[(players['p3'], players['p1'], players['p4'], players['p2'])] + played_matches[(players['p4'], players['p2'], players['p3'], players['p1'])], 0, ''],  
        (players['p4'], players['p2'], players['p1'], players['p3']): [played_matches[(players['p4'], players['p2'], players['p1'], players['p3'])] + played_matches[(players['p1'], players['p3'], players['p4'], players['p2'])], 0, ''],
    }

    reduced_played_matches = dict(sorted(reduced_played_matches.items(), key=lambda item: item[1], reverse=False))

    # filter positions
    for km, vm in reduced_played_matches.items():
        for kp, vp in player_dict.items():
            if vp == '':
                vm[1] += 1
            elif vp == 'atk':
                if kp == km[0] or kp == km[2]:
                    vm[1] += 1
            elif vp == 'def':
                if kp == km[1] or kp == km[3]:
                    vm[1] += 1

    for v in reduced_played_matches.values():
        if v[1] == 4:
            v[1] = True
        else:
            v[1] = False

    for k, v in player_dict.items():
        for i in players_data:
            if k == i.user.id:
                player_dict[k] = i.user
                break

    for k, v in reduced_played_matches.items():
        v[2] = f'{player_dict[k[0]]} + {player_dict[k[1]]} vs {player_dict[k[2]]} + {player_dict[k[3]]}'

    return reduced_played_matches