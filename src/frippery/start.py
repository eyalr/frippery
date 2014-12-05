from flask import g

def finalize_attendees(event_id, ticket_class_id):
    attendee_data = g.eb_api.get(
        'events/%d/attendees' % (event_id,)
    ).data['attendees']
    attendees = [
        {
            'first': attendee['profile']['first_name'],
            'last': attendee['profile']['last_name'],
            'email': attendee['profile']['email'],
        }
        for attendee in attendee_data
        if attendee['ticket_class_id'] == ticket_class_id
    ]
    return attendees
