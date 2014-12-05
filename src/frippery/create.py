import datetime
import json
from flask import g


def create_new_event(form_values):
    # user_id = g.user_id
    # import pdb; pdb.set_trace()
    organizer_id = g.eb_api.get('/v3/users/me/organizers')
    start_date = form_values['event_start_date'] + "T" + form_values['event_start_time'] + "Z"
    end_date = form_values['event_end_date'] + "T" + form_values['event_end_time'] + "Z"
    create_data = {
        'event.name.html': form_values['event_name'],
        'event.currency': 'USD',
        'event.description.html': form_values['event_description'],
        'event.start.utc': start_date,
        'event.start.timezone': 'America/Los_Angeles',
        'event.end.utc': end_date,
        'event.end.timezone': 'America/Los_Angeles',
        'event.organizer_id': organizer_id,
        'event.online_event': True,
    }

    response_from_api = g.eb_api.post("events/", create_data)
    event_id = response_from_api.eid
    ticket_post_path = 'v3/events/' + event_id + "/ticket_classes"
    ticket_post_information = {
        ticket_class.name: g.frippery_app,
        ticket_class.quantity_total: "",
        ticket_class.free: True,
    }
    g.eb_api.post(ticket_post_path,)
    response_from_api = external_requests.post("https://www.eventbrite.com/xml/events/publish/", event_id)

# start/end timezones
# ^^^ this is in "Olson Format": http://en.wikipedia.org/wiki/List_of_tz_database_time_zones
# ^^^ 3rd column from left
# user id/authorization of some sort
# ^^^ use eventbriteapi that gets passed in - eyal

""" eyal: I succesfully created an event like so...
created_event = eventbriteapi.post(
    'events/',
    {
        'event.name.html': 'testing',
        'event.currency': 'USD',
        'event.description.html': 'test_description',
        'event.start.utc': '2014-12-18T16:00:00Z',
        'event.start.timezone': 'America/Los_Angeles',
        'event.end.utc': '2014-12-18T23:00:00Z',
        'event.end.timezone': 'America/Los_Angeles',
        'event.organizer_id': '7803975089',
        'event.online_event': True,
    },
)
my_new_event_id = created_event['id']
"""

""" jay: Ok, Once you've created an event you need to store it into redis
do that with:

    import storage
    storage.add_event(
        user_id,
        event_id,
        {
            'name': 'testing',
            'descr': 'test_description',
            'type': 'secret-santa',
        }
    )

"""
