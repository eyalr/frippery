from flask import g
import json
import redis

import settings

EVENT_STATUS_NEW = 1
EVENT_STATUS_STARTED = 2

def _get_redis_client():
    redis_client = getattr(g, 'redis', None)
    if redis_client is not None:
        return redis_client
    g.redis = redis.Redis(**settings.REDIS_INIT)

    return g.redis

def _user_key(user_id):
    return 'USER::%s' % (user_id,)

def _event_key(event_id):
    return 'EVENT::%s' % (event_id,)

def _view_key(event_id):
    return 'VIEW::%s' % (event_id,)

def add_event(user_id, event_id, data):
    """
        data = {
            'name': 'EVENT NAME',
            'descr': 'EVENT DESCR',
        }
    """
    redis_client = _get_redis_client()
    redis_client.hset(
        _user_key(user_id),
        event_id,
        EVENT_STATUS_NEW,
    )
    data['user_id'] = user_id
    data['event_id'] = event_id
    redis_client.hmset(
        _event_key(event_id),
        data,
    )

def list_events(user_id):
    redis_client = _get_redis_client()
    # TODO: make more efficient in pipeline
    result = [
        (
            int(event_id),
            int(status),
            redis_client.hgetall(_event_key(event_id)),
        )
        for event_id, status in redis_client.hgetall(
            _user_key(user_id),
        ).iteritems()
    ]
    result.sort()
    return result

def get_event(event_id):
    redis_client = _get_redis_client()
    return redis_client.hgetall(_event_key(event_id))

def start_event(user_id, event_id):
    redis_client = _get_redis_client()
    redis_client.hset(_user_key(user_id), event_id, EVENT_STATUS_STARTED)

def save_event_view(event_id, view_data):
    redis_client = _get_redis_client()
    redis_client.set(_view_key(event_id), json.dumps(view_data))

def load_event_view(event_id):
    redis_client = _get_redis_client()
    ret = redis_client.get(_view_key(event_id))
    if ret is None:
        return None
    else:
        return json.loads(ret)
