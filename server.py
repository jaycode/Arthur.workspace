import os
import tornado.ioloop
import tornado.web
import sockjs.tornado
from app import app

if __name__ == '__main__':
    app.listen(os.getenv('VCAP_APP_PORT', 49152))
    tornado.ioloop.IOLoop.instance().start()

# import os
# import sys
# parent_dir = os.path.abspath(os.path.dirname(__file__))
# vendor_dir = os.path.join(parent_dir, 'vendor')
# sys.path.append(vendor_dir)

# print "one"
# from tornado.wsgi import WSGIContainer
# from tornado.ioloop import IOLoop
# from tornado.web import FallbackHandler, RequestHandler, Application
# from flask import Flask, render_template, jsonify, request
# from app import app

# print "two"
# tr = WSGIContainer(app)

# application = Application([
# (r".*", FallbackHandler, dict(fallback=tr)),
# ])
# print "three"

# print "starting..."
# if __name__ == "__main__":
#     PORT = int(os.getenv('VCAP_APP_PORT', 49152))
#     HOST = str(os.getenv('VCAP_APP_HOST', 'localhost'))
#     print("Start serving at port %i" % PORT)
#     application.listen(PORT)
#     IOLoop.instance().start()
# print "four"


# import os
# try:
#   from SimpleHTTPServer import SimpleHTTPRequestHandler as Handler
#   from SocketServer import TCPServer as Server
# except ImportError:
#   from http.server import SimpleHTTPRequestHandler as Handler
#   from http.server import HTTPServer as Server

# # Read port selected by the cloud for our application
# PORT = int(os.getenv('PORT', 8000))
# # Change current directory to avoid exposure of control files
# os.chdir('static')

# httpd = Server(("", PORT), Handler)
# try:
#   print("Start serving at port %i" % PORT)
#   httpd.serve_forever()
# except KeyboardInterrupt:
#   pass
# httpd.server_close()