import json
import requests as external_requests


def create_new_event(form_values):
    json_blob = json.dumps(form_values)
    response_from_api = external_requests.post("https://www.eventbrite.com/xml/events/composite-create/", json_blob)
    import pdb; pdb.set_trace()
    event_id = response_from_api.eid
    response_from_api = external_requests.post("https://www.eventbrite.com/xml/events/publish/", event_id)


# figure out how to pass in:
# api key with request to api
# ^^^ use eventbriteapi that gets passed in - eyal
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
