import json
import requests as external_requests


def create_new_event(form_values):
    json_blob = json.dumps(form_values)
    response_from_api = external_requests.post("https://www.eventbrite.com/xml/events/composite-create/", json_blob)
    event_id = response_from_api.eid
    response_from_api = external_requests.post("https://www.eventbrite.com/xml/events/publish/", event_id)


# figure out how to pass in:
# api key with request to api
# start/end timezones
# user id/authorization of some sort
