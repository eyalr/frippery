import datetime
import json
import storage
import string
from flask import g


def create_new_event(form_values):
    user_id = g.user_id
    organizer_api_data = g.eb_api.get('/v3/users/me/organizers')
    organizer_ids = organizer_api_data.data['organizers']
    if len(organizer_ids) >= 1:
        organizer_id = organizer_ids[0]['id']
    elif len(organizer_ids) == 0:
        organizer = g.eb_api.post('organizers/', {
            'organizer.name': 'Organizer',
            'organizer.description.html': '',
        })
        organizer_id = organizer.data['id']

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

    event_id = response_from_api.data['id']
    ticket_post_path = '/v3/events/' + event_id + "/ticket_classes/"
    ticket_post_information = {
        'ticket_class.name': '%s participant' % (string.capwords(g.frippery_app.replace('-', ' ')),),
        'ticket_class.quantity_total': form_values['ticket_quantity'],
        'ticket_class.free': 'on',
    }
    ticket_info = g.eb_api.post(ticket_post_path, ticket_post_information)
    ticket_class_id = ticket_info.data['id']
    path_to_publish = "/v3/events/" + event_id + "/publish/"
    response_from_api = g.eb_api.post(path_to_publish, {})
    storage.add_event(
        user_id,
        event_id,
        {
            'name': form_values['event_name'],
            'descr': form_values['event_description'],
            'type': g.frippery_app,
            'ticket_class': ticket_class_id,
        }
    )
