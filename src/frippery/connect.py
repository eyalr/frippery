from flask import g

def connect_event(event_id):
    ticket_data = g.eb_api.get(
        'events/%d/ticket_classes' % (int(event_id),)
    ).data['ticket_classes']
    ticket_classes = {
        d['id']: {
            'name': d['name'],
            'quantity_sold': d['quantity_sold'],
        } for d in ticket_data
    }
    return ticket_classes
