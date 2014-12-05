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
from flask_oauthlib.client import OAuth, OAuthException
from werkzeug import security

import create

import settings

app = Flask(__name__)
app.secret_key = 'development'
oauth = OAuth(app)

class _NOT_DEFINED(object):
    pass

eventbriteapi = _NOT_DEFINED

app_config = {
    'tourney': {
        'consumer_key': 'JYUY5CEW6XFOIALPTA',
        'consumer_secret': settings.tourney_secret_key,
    },
    'secret-santa': {
        'consumer_key': 'Z5HCI737VIWT2DRTAK',
        'consumer_secret': settings.secret_santa_secret_key,
    },
}


def _init_eventbriteapi():
    global eventbriteapi
    if eventbriteapi is _NOT_DEFINED:
        eventbriteapi = oauth.remote_app(
            'eventbrite',
            consumer_key=app_config[g.frippery_app]['consumer_key'],
            consumer_secret=app_config[g.frippery_app]['consumer_secret'],
            request_token_params={
                'state': lambda: security.gen_salt(10)
            },
            base_url='https://www.eventbriteapi.com/v3/',
            request_token_url=None,
            access_token_method='POST',
            access_token_url='https://www.eventbrite.com/oauth/token',
            authorize_url='https://www.eventbrite.com/oauth/authorize'
        )
        eventbriteapi.tokengetter(lambda *args: session.get('eventbrite_token'))


@app.route('/', methods=['GET'])
def index():
    _init_eventbriteapi()
    if 'eventbrite_token' in session:
        me = eventbriteapi.get('users/me')
        return jsonify(me.data)
    # this is where user lands to enter their form information
    return render_template('index.html')

@app.route('/login')
def login():
    _init_eventbriteapi()
    return eventbriteapi.authorize(
        callback=url_for('authorized', _external=True),
    )

@app.route('/events')
def authorized():
    _init_eventbriteapi()
    resp = eventbriteapi.authorized_response()
    if resp is None or isinstance(resp, OAuthException):
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description']
        )
    session['eventbrite_token'] = (resp['access_token'], '')
    me = eventbriteapi.get('users/me')
    return jsonify(me.data)

@app.before_request
def before_request():
    request.host
    if 'secret-santa' in request.host.lower():
        g.frippery_app = 'secret-santa'
    else:
        g.frippery_app = 'tourney'

@app.route('/create', methods=['GET'])
def create_view():
    return render_template('create.html')

@app.route('/publish', methods=['POST'])
def submit_new_event():
    create.create_new_event(request.values.to_dict())
    return redirect('/events')

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)

