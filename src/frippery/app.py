import re

from flask import (
    Flask,
    g,
    redirect,
    render_template,
    request,
)

import create


app = Flask(__name__)

@app.before_request
def before_request():
    request.host
    if 'secret-santa' in request.host.lower():
        g.frippery_app = 'secret-santa'
    else:
        g.frippery_app = 'tourney'

@app.route('/', methods=['GET'])
def index():
    return render_template('index.html')

@app.route('/create', methods=['GET'])
def create_view():
    return render_template('create.html')

@app.route('/publish', methods=['POST'])
def submit_new_event():
    create.create_new_event(request.values.to_dict())
    return redirect('/events')

if __name__ == '__main__':
    app.run('0.0.0.0', debug=True)

