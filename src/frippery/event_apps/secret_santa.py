import random

def create_event_view(event, attendees):
    random.shuffle(attendees)
    return attendees


def get_context(event, event_view):
    num = len(event_view)
    gifts = []
    for i in xrange(num):
        a = event_view[i]
        b = event_view[(i + 1) % num]

        gifts.append((
            "%s %s" % (a['first'], a['last']),
            "%s %s" % (b['first'], b['last']),
        ))

    return locals()
