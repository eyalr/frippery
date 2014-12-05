import math
import random

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
