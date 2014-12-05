from flask import (
    g,
    jsonify,
    request,
    session,
)
from flask_oauthlib.client import OAuth, OAuthException
from werkzeug import security

import settings

def initialize(app):
    app.secret_key = 'development'
    oauth = OAuth(app)

    host_eb_apis = {
        'tourney': oauth.remote_app(
            'eventbrite-tourney',
            consumer_key='JYUY5CEW6XFOIALPTA',
            consumer_secret=settings.tourney_secret_key,
            request_token_params={
                'state': lambda: security.gen_salt(10)
            },
            base_url='https://www.eventbriteapi.com/v3/',
            request_token_url=None,
            access_token_method='POST',
            access_token_url='https://www.eventbrite.com/oauth/token',
            authorize_url='https://www.eventbrite.com/oauth/authorize',
        ),
        'secret-santa': oauth.remote_app(
            'eventbrite-ss',
            consumer_key='Z5HCI737VIWT2DRTAK',
            consumer_secret=settings.secret_santa_secret_key,
            request_token_params={
                'state': lambda: security.gen_salt(10)
            },
            base_url='https://www.eventbriteapi.com/v3/',
            request_token_url=None,
            access_token_method='POST',
            access_token_url='https://www.eventbrite.com/oauth/token',
            authorize_url='https://www.eventbrite.com/oauth/authorize',
        ),
    }
    for _api in host_eb_apis.values():
        _api.tokengetter(lambda *args: session.get('eventbrite_token'))

    return host_eb_apis

def authorize(eb_api):
    resp = eb_api.authorized_response()
    if resp is None or isinstance(resp, OAuthException):
        return 'Access denied: reason=%s error=%s' % (
            request.args['error_reason'],
            request.args['error_description'],
        )
    session['eventbrite_token'] = (resp['access_token'], '')
    session['eventbrite_me'] = eb_api.get('users/me').data
    ''' users/me data format
        {
        "emails": [
            {
            "email": "eyal+jay+mica+nicolez@eventbrite.com",
            "primary": true,
            "verified": false
            }
        ],
        "first_name": null,
        "id": "131185252373",
        "last_name": null,
        "name": "eyal+jay+mica+nicolez@eventbrite.com"
        }
    '''
    return None

def is_logged_in():
    if 'eventbrite_token' not in session or 'eventbrite_me' not in session:
        return False

    g.user_id = int(session['eventbrite_me']["id"])
    return True

def logout():
    if 'eventbrite_token' in session:
        del session['eventbrite_token']

    if 'eventbrite_me' in session:
        del session['eventbrite_me']

