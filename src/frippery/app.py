import re

from flask import (
    Flask,
    jsonify,
    g,
    redirect,
    render_template,
    request,
    session,
    url_for,
)
from flask_oauthlib.client import OAuthException

import auth
import connect
import create
import event_apps
import mail
import start
import storage

import settings

app = Flask(__name__)
eventbite_apis = auth.initialize(app)

@app.before_request
def before_request():
    if 'secret-santa' in request.host.lower():
        g.frippery_app = 'secret-santa'
    else:
        g.frippery_app = 'tourney'
    g.eb_api = eventbite_apis[g.frippery_app]


@app.route('/', methods=['GET'])
def index():
    if auth.is_logged_in():
        return redirect('/events')
    return render_template('index.html')

@app.route('/dummy_mail')
def dummy_mail():
    mail.send_email(
        'jay@evbqa.com',
        'HELLLLOOOO',
        render_template(
            'secret-santa-notify.eml',
            gifter="Jay",
            event_name="Bob's Secret Santa",
            giftee="Eyal",
            ),
    )
    return 'ok'

@app.route('/dummy_create')
def test_data():
    if not auth.is_logged_in():
        return redirect('/')
    storage.add_event(g.user_id, 456, {'name': 'EVENT!', 'descr': 'DESCRIPERINO', 'type': 'secret-santa'})
    storage.start_event(g.user_id, 456)
    storage.save_event_view(456, [[
        {
            'first': 'Jay',
            'last': 'Chan',
            'email': 'jay@evbqa.com',
        },
        {
            'first': 'Eyal',
            'last': 'Reuveni',
            'email': 'eyal@evbqa.com',
        },
        {
            'first': 'Mica',
            'last': 'Swyers',
            'email': 'mica@evbqa.com',
        },
        {
            'first': 'Nicole',
            'last': 'Zuckercorn',
            'email': 'nicolez@evbqa.com',
        },

    ], {'notified': False}])
    storage.add_event(g.user_id, 457, {'name': 'EVENT DOS!', 'descr': 'OTHER ONE!', 'type': 'tourney'})

    storage.add_event(g.user_id, 458, {'name': 'NUMERO 3', 'descr': 'ANOTHER!', 'type': 'tourney'})
    storage.start_event(g.user_id, 458)
    storage.save_event_view(458, [[
        {
            'first': 'Jay',
            'last': 'Chan',
            'email': 'jay@evbqa.com',
        },
        {
            'first': 'Eyal',
            'last': 'Reuveni',
            'email': 'eyal@evbqa.com',
        },
        {
            'first': 'Mica',
            'last': 'Swyers',
            'email': 'mica@evbqa.com',
        },
        {
            'first': 'Nicole',
            'last': 'Zuckercorn',
            'email': 'nicolez@evbqa.com',
        },
        {
            'first': 'Kevin',
            'last': 'Hartz',
            'email': 'kevin@dummy.com',
        },
        {
            'first': 'Julia',
            'last': 'Hartz',
            'email': 'julia@dummy.com',
        },

    ], {'1:2': 2, '4:5': 5, '0:2':2, '3:5':3, '2:3': 3}])
    return str(storage.list_events(g.user_id))

@app.route('/login')
def login():
    if auth.is_logged_in():
        return redirect('/events')
    return g.eb_api.authorize(callback=url_for('authorize', _external=True))

@app.route('/authorize')
def authorize():
    auth_error = auth.authorize(g.eb_api)
    if auth_error is None:
        return redirect('/events')
    else:
        return auth_error

@app.route('/events')
def events():
    if not auth.is_logged_in():
        return redirect('/')
    events = storage.list_events(g.user_id)
    from storage import (
        EVENT_STATUS_NEW,
        EVENT_STATUS_STARTED,
    )
    return render_template('events.html', **locals())

@app.route('/<int:event_id>')
def view_event(event_id):
    # don't have to be logged in, but still get logged in status
    auth.is_logged_in()

    event = storage.get_event(event_id)
    event_view = storage.load_event_view(event_id)
    event_type = event['type']

    # pretend user isn't logged in
    if hasattr(g, 'userid') and event['user_id'] != g.user_id:
        delattr(g, 'user_id')

    g.frippery_app = event_type

    if event_type == 'secret-santa':
        context = event_apps.secret_santa.get_context(event, event_view)
        return render_template('secret-santa.html', event_id=event_id, **context)
    elif event_type == 'tourney':
        context = event_apps.tourney.get_context(event, event_view)
        return render_template('tourney.html', event_id=event_id, **context)
    else:
        return "UNKNOWN EVENT TYPE"

@app.route('/action/<int:event_id>/<string:method>')
def action(event_id, method):
    if not auth.is_logged_in():
        return redirect('/')

    event = storage.get_event(event_id)
    event_type = event['type']

    if hasattr(g, 'userid') and event['user_id'] != g.user_id:
        return "NOT YOUR EVENT"

    if event_type == 'secret-santa':
        app = event_apps.secret_santa
    elif event_type == 'tourney':
        app = event_apps.tourney
    else:
        return "UNKNOWN EVENT TYPE"

    method = getattr(app, method, None)
    if method is None:
        return "UNKNOWN METHOD"

    method(event_id, **request.values.to_dict())
    return redirect('/%s' % (event_id,))


@app.route('/create', methods=['GET'])
def create_view():
    if not auth.is_logged_in():
        return redirect('/')
    return render_template('create.html')

@app.route('/publish', methods=['POST'])
def submit_new_event():
    if not auth.is_logged_in():
        return redirect('/')
    create.create_new_event(request.values.to_dict())
    return redirect('/events')

@app.route('/start/<int:event_id>', methods=['GET'])
def start_event(event_id):
    if not auth.is_logged_in():
        return redirect('/')
    storage.start_event(g.user_id, event_id)

    event_data = storage.get_event(event_id)
    event_type = event_data['type']
    if event_type == 'secret-santa':
        app = event_apps.secret_santa
    elif event_type == 'tourney':
        app = event_apps.tourney
    ticket_class_id = event_data['ticket_class']

    attendees = start.finalize_attendees(event_id, ticket_class_id)
    storage.save_event_view(
        event_id,
        app.create_event_view(event_data, attendees),
    )
    return redirect('/%d' % (event_id,))

@app.route('/connect', methods=['GET', 'POST'])
def connect_event():
    if not auth.is_logged_in():
        return redirect('/')
    input_data = request.values.to_dict()
    event_id = input_data.get('eid') or '0'
    if 'http' in event_id or 'eventbrite' in event_id:
        event_id = re.search('/e/([0-9]+)', event_id).group(1)
    event_id = int(event_id)
    ticket_class = input_data.get('ticket_class')

    if ticket_class is None:
        ticket_classes = connect.connect_event(event_id)
    else:
        ticket_classes = {}

    # If only one ticket class, no need to prompt them to select one.
    if len(ticket_classes) == 1:
        ticket_class = ticket_classes.keys()[0]

    if ticket_class:
        event_data = g.eb_api.get(
            'events/%d' % (int(event_id),)
        ).data
        storage.add_event(
            g.user_id,
            int(event_id),
            {
                'name': event_data['name']['text'],
                'descr': event_data['description']['text'],
                'type': g.frippery_app,
                'ticket_class': int(ticket_class),
            },
        )

    if ticket_class is None:
        return render_template(
            'connect.html',
            ticket_classes=ticket_classes,
            event_id=event_id,
        )
    else:
        return redirect('/events')

@app.route('/logout')
def logout():
    auth.logout()
    return redirect('/')

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)

