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
import create
import event_apps
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

@app.route('/dummy_create')
def test_data():
    if not auth.is_logged_in():
        return redirect('/')
    storage.add_event(g.user_id, 456, {'name': 'EVENT!', 'descr': 'DESCRIPERINO', 'type': 'secret-santa'})
    storage.start_event(g.user_id, 456)
    storage.save_event_view(456, [
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

    ])
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

    g.frippery_app = event_type

    if event_type == 'secret-santa':
        context = event_apps.secret_santa.get_context(event, event_view)
        return render_template('secret-santa.html', **context)
    elif event_type == 'tourney':
        context = event_apps.tourney.get_context(event, event_view)
        return render_template('tourney.html', **context)
    else:
        return "UNKNOWN EVENT TYPE"

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

@app.route('/logout')
def logout():
    auth.logout()
    return redirect('/')

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)

