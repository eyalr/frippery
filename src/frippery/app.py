from flask import Flask
from flask import redirect
from flask import render_template
from flask import request

import create
app = Flask(__name__)


@app.route('/create', methods=['GET'])
def create_view():
    import pdb; pdb.set_trace()
    return render_template('create.html')

@app.route('/publish', methods=['POST'])
def submit_new_event():
    create.create_new_event(request.values.to_dict())
    return redirect('/events')

if __name__ == '__main__':
    app.run(debug=True)

