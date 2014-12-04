import json
import requests as external_requests

from flask import Flask
from flask import render_template
from flask import request
app = Flask(__name__)

@app.route('/', methods=['GET'])
def index():
    # this is where user lands to enter their form information
    return render_template('index.html')

@app.route('/create', methods=['GET'])
def submit_new_event():
    json_blob = json.dumps(request.values.to_dict())
    response_from_api = external_requests.post("https://www.eventbrite.com/xml/events/composite-create/", json_blob)
    event_id = response_from_api.eid
    response_from_api = external_requests.post("https://www.eventbrite.com/xml/events/publish/", event_id)
    return "Submitted! Come back again when your event sales date is over!"
if __name__ == '__main__':
    app.run(debug=True)



# figure out how to pass in:
# api key with request to api
# start/end timezones
# user id/authorization of some sort
