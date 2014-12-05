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

eventbriteapi = oauth.remote_app(
    'eventbrite',
    consumer_key='JYUY5CEW6XFOIALPTA',
    consumer_secret=settings.secret_key,
    request_token_params={
        'state': lambda: security.gen_salt(10)
    },
    base_url='https://www.eventbriteapi.com/v3/',
    request_token_url=None,
    access_token_method='POST',
    access_token_url='https://www.eventbrite.com/oauth/token',
    authorize_url='https://www.eventbrite.com/oauth/authorize'
)



@app.route('/', methods=['GET'])
def index():
    if 'eventbrite_token' in session:
        me = eventbriteapi.get('users/me')
        return jsonify(me.data)
    # this is where user lands to enter their form information
    return render_template('index.html')

@app.route('/login')
def login():
    return eventbriteapi.authorize(
        callback=url_for('authorized', _external=True),
    )

@app.route('/events')
def authorized():
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

@eventbriteapi.tokengetter
def get_eventbrite_oauth_token():
    return session.get('eventbrite_token')

@app.route('/create', methods=['GET'])
def create_view():
    return render_template('create.html')

@app.route('/publish', methods=['POST'])
def submit_new_event():
    create.create_new_event(request.values.to_dict())
    return redirect('/events')

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)

