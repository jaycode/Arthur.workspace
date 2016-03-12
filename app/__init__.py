"""
Workspace module application.
"""
import tornado.ioloop
import tornado.web

import sockjs.tornado
import pdb
import json
from pymongo import mongo_client
from pymongo import database
from pymongo.database import Database
import logging
from mod_cmd.controllers import WorkspaceConnection
import config
from redis import Redis
from libs.redis_session.for_tornado import RedisSessionStore

class MongoClient(mongo_client.MongoClient):
    """Replace 'db' with config.MONGO_DBNAME to make this similar to Flask-PyMongo
    """

    def __getattr__(self, name):
        if name == 'db':
            name = config.MONGO_DBNAME
        attr = super(MongoClient, self).__getattr__(name)
        if isinstance(attr, database.Database):
            return Database(self, name)
        return attr

    def __getitem__(self, item):
        if item == 'db':
            item = config.MONGO_DBNAME
        attr = super(MongoClient, self).__getitem__(item)
        if isinstance(attr, database.Database):
            return Database(self, item)
        return attr


port = ''
if config.MONGO_PORT:
    port = ':%s' % config.MONGO_PORT
uri = "mongodb://%s:%s@%s%s/%s?authMechanism=SCRAM-SHA-1" % \
      (config.MONGO_USERNAME, config.MONGO_PASSWORD, config.MONGO_HOST, port, config.MONGO_DBNAME)
mongo = MongoClient(uri)

logging.getLogger().setLevel(logging.DEBUG)

WorkspaceRouter = sockjs.tornado.SockJSRouter(WorkspaceConnection, '/')

class IndexHandler(tornado.web.RequestHandler):
    """Just a page to show if server is up"""
    def get(self):
        self.render('index.html')

class Application(tornado.web.Application):
    config = {} # for simpler config access.
    session_store = None # Session store, not the actual session (session can only be set right after first request).
    def __init__(self, config):
        handlers = [(r"/", IndexHandler)] + WorkspaceRouter.urls
        self.config = config
        settings = {
            "cookie_secret": self.config['SECRET_KEY']
        }
        redis_conn = Redis(host=self.config['REDIS_HOST'], port=self.config['REDIS_PORT'], password=self.config['REDIS_PASSWORD'])
        self.session_store = RedisSessionStore(redis_conn)
        super(Application, self).__init__(handlers, **settings)

attrs = filter(lambda x: x[0] != '_' and str.isupper(x[0]), dir(config))
mapped_config = {}
for attr in attrs:
    mapped_config[attr] = getattr(config, attr)
app = Application(mapped_config)

