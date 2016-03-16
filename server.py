import os
import tornado.ioloop
import tornado.web
import sockjs.tornado
from app import app

if __name__ == '__main__':
    # app.listen(os.getenv('VCAP_APP_PORT', 49152))
    app.listen(49152)
    tornado.ioloop.IOLoop.instance().start()
