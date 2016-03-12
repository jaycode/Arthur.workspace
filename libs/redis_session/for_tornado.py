"""
Simple Redis Session for Tornado.

Based on the code by Mike Moore(http://webofmike.com/tornado-sessions-with-redis/).

Adjusted to make it more similar to Flask's RedisSession. The idea is so we can share
the session between Flask and Tornado app.

Also added some docstring tests. Run this script to test its features. Make sure to have
a Redis server up and ready prior to testing.
"""

try:
    import cPickle as pickle
except:
    import pickle
from uuid import uuid4
import time
import pdb
from datetime import timedelta

class RedisSessionStore:
    """Session store to be passed to Session object.
    """
    def __init__(self, redis_connection, **options):
        """Initialize SessionStore.

        Args:
            redis_connection: Redis instance.
            key_prefix: Default to 'session'.
            expire: How many microseconds till session expiration. Defaults to 1 day.
            safe_mode: When set to True, needs to run method :_save(): to actually
                       save the session.

        """
        self.options = {
            'key_prefix': 'session',
            'expire': timedelta(days=1),
            'safe_mode': False
        }
        self.options.update(options)
        self.redis = redis_connection

    def prefixed(self, sid):
        return '%s:%s' % (self.options['key_prefix'], sid)

    def generate_sid(self, ):
        return uuid4().get_hex()

    def get_session(self, sid):
        data = self.redis.get(self.prefixed(sid))
        session = pickle.loads(data) if data else dict()
        return session

    def set_session(self, sid, session_data):
        expiry = self.options['expire']
        self.redis.setex(self.prefixed(sid), pickle.dumps(session_data),
                         self.options['expire'])
        if expiry:
            self.redis.expire(self.prefixed(sid), expiry)

    def delete_session(self, sid):
        self.redis.delete(self.prefixed(sid))

class Session:
    """Session object we can use in many types of WSGI Python apps.

    >>> from redis import Redis
    >>> redis_conn = Redis('192.168.59.103', 6379)
    >>> session_store = RedisSessionStore(redis_conn, safe_mode=True)
    >>> sessionid = 'test_session_id'
    >>> session = Session(session_store, sessionid)
    >>> session['test_data'] = 'test_value'

    How is the object represented?
    >>> print(session)
    {'test_data': 'test_value'}

    Currently, this session object is dirty (i.e. not saved into Redis).
    >>> session.dirty
    True

    Commit the change with :_save(): method.
    >>> session._save()
    >>> session.dirty
    False

    >>> print(session['test_data'])
    test_value

    Confirm that the value is stored by manually connect to Redis server
    and get the value of key "session:test_session_id", unpickle it, and
    get its "test_data" value.
    >>> # pdb.set_trace()
    >>> pickled = redis_conn.get("session:test_session_id")
    >>> data = pickle.loads(pickled)
    >>> print(data['test_data'])
    test_value

    Alright, addition works, what about update?
    We will also try out option "safe_mode = False" to make it more
    similar to Flask's RedisSession.
    >>> session_store = RedisSessionStore(redis_conn)
    >>> sessionid = 'test_session_id'
    >>> session = Session(session_store, sessionid)
    >>> session['test_data'] = 'test_value2'
    >>> print(session['test_data'])
    test_value2

    Again confirm by manual connection
    >>> pickled = redis_conn.get("session:test_session_id")
    >>> data = pickle.loads(pickled)
    >>> print(data['test_data'])
    test_value2

    How about deletion?
    >>> session.pop('test_data')
    >>> 'test_data' in session
    False

    Confirm by manual connection
    >>> pickled = redis_conn.get("session:test_session_id")
    >>> data = pickle.loads(pickled)
    >>> 'test_data' in data
    False

    """
    def __init__(self, session_store, sessionid=None):
        """Initialize session storage.

        Args:
            session_store: Pass instance of RedisSessionStore here.
            sessionid: Session ID. Different framework may treat this differently.
                       In Tornado SockJS, for example, this is only available from 
                       :on_open: method inside :sockjs.tornado.SockJSConnection:, variable
                       :info:.
        """
        self._store = session_store
        self._sessionid = sessionid if sessionid else self._store.generate_sid()
        self._sessiondata = self._store.get_session(self._sessionid)
        self.dirty = False

    def clear(self):
        self._store.delete_session(self._sessionid)

    @property
    def sessionid(self):
        return self._sessionid

    def __getitem__(self, key):
        return self._sessiondata[key]

    def __setitem__(self, key, value):
        self._sessiondata[key] = value
        self._dirty()
        if not self._store.options['safe_mode']:
            self._save()

    def __delitem__(self, key):
        del self._sessiondata[key]
        self._dirty()
        if not self._store.options['safe_mode']:
            self._save()

    def __len__(self):
        return len(self._sessiondata)

    def __contains__(self, key):
        return key in self._sessiondata

    def __iter__(self):
        for key in self._sessiondata:
            yield key

    def __repr__(self):
        return self._sessiondata.__repr__()

    def __del__(self):
        if self.dirty:
            self._save()

    def _dirty(self):
        self.dirty = True

    def _save(self):
        self._store.set_session(self._sessionid, self._sessiondata)
        self.dirty = False

    def pop(self, key):
        del self._sessiondata[key]
        self._dirty()
        if not self._store.options['safe_mode']:
            self._save()

if __name__ == '__main__':
    import doctest
    import os, sys, inspect
    import pdb
    # This needs to be included here to ensure path loaded from file dir.
    base_path = os.path.realpath(
        os.path.abspath(
            os.path.join(
                os.path.split(
                    inspect.getfile(
                        inspect.currentframe()
                    )
                )[0]
            )
        )
    )
    doctest.testmod()