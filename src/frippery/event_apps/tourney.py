import math
import random

import storage

def create_event_view(event, attendees):
    random.shuffle(attendees)
    return [attendees, {}]

def get_context(event, event_view):

    attendees, results = event_view
    players = list(enumerate(
        '%s %s' % (x['first'], x['last'])
        for x in attendees
    ))

    num = len(players)
    if num == 1:
        rounds = 0
    else:
        rounds = int(math.log(num - 1, 2) + 1)

    columns = [[] for i in xrange(rounds + 1)]

    def _recur_split(players, depth=0):
        num = len(players)
        half = num / 2

        if num == 1:
            return players[0][0]
        else:
            a = _recur_split(players[:half], depth + 1)
            b = _recur_split(players[half:], depth + 1)
            res_key = '%s:%s' % tuple(sorted([a, b]))
            winner = results.get(res_key, None)
            # account for byes
            if half == 1 and depth >= rounds - 1:
                columns[depth + 1].append([('', 1)])
            columns[depth + 1].append([
                (a, half),
                (b, num - half),
            ])
            return winner

    winner = _recur_split(players)
    columns[0].append([(winner, num)])

    columns = list(reversed(columns))

    # [[[0], [3, 2]], [[5], [1, 4]]]
    span = int(12 / (rounds + 1))
    count = len

    return locals()

def set_result(event_id, player_1='None', player_2='None', winner='None'):
    if player_1 == 'None' or player_2 == 'None':
        return

    event_view = storage.load_event_view(event_id)
    event_view[1][
        '%s:%s' % tuple(sorted([int(player_1), int(player_2)]))
    ] = int(winner)

    storage.save_event_view(event_id, event_view)

def reset(event_id):
    event_view = storage.load_event_view(event_id)
    event_view[1] = {}

    storage.save_event_view(event_id, event_view)
