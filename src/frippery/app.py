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
import storage

import settings

app = Flask(__name__)
eventbite_apis = auth.initialize(app)

@app.before_request
def before_request():
    if 'secret-santa' in request.host.lower():
        g.frippery_app = 'secret-santa'
        g.frippery_app_pretty = 'secret santa'
    else:
        g.frippery_app = 'tourney'
        g.frippery_app_pretty = 'tournament'
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
    storage.add_event(g.user_id, 457, {'name': 'EVENT DOS!', 'descr': 'OTHER ONE!', 'type': 'secret-santa'})
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

