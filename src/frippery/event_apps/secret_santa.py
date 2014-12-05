from flask import render_template
import random

import mail
import storage

def create_event_view(event, attendees):
    random.shuffle(attendees)
    return (attendees, {'notified': False})


def get_context(event, event_view):
    attendees, extras = event_view
    num = len(attendees)
    gifts = []
    for i in xrange(num):
        a = attendees[i]
        b = attendees[(i + 1) % num]

        gifts.append((
            "%s %s" % (a['first'], a['last']),
            "%s %s" % (b['first'], b['last']),
        ))

    notified = extras['notified']

    return locals()

def notify(event_id):
    event = storage.get_event(event_id)
    event_view = storage.load_event_view(event_id)
    attendees, extras = event_view

    num = len(attendees)
    gifts = []
    for i in xrange(num):
        gifter = attendees[i]
        giftee = attendees[(i + 1) % num]

        mail.send_email(
            gifter['email'],
            'You are a secret santa!',
            render_template(
                'secret-santa-notify.eml',
                gifter=gifter['first'],
                event_name=event['name'],
                giftee='%s %s' % (giftee['first'], giftee['last']),
            ),
        )

    event_view[1]['notified'] = True

    storage.save_event_view(event_id, event_view)
