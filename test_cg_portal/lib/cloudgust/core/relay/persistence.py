import re
import unicodedata
from socketio import socketio_manage
from socketio.namespace import BaseNamespace
from socketio.mixins import RoomsMixin, BroadcastMixin
from werkzeug.exceptions import NotFound
from gevent import monkey
from socketio.server import SocketIOServer
from relay import RelayTransport
from ..events import Events
import logging

logging.basicConfig(level=logging.DEBUG)

from flask import Flask, Response, request, render_template, url_for, redirect

monkey.patch_all()

class PersistentTransport(RelayTransport):
	def __init__(self):
		super(PersistentTransport, self).__init__()
		self.app = Flask("PersistentTransport")
		self.app.debug = True
		self.port = 5000

		self._initialize()

	def _initialize(self):
		print 'Listening on http://127.0.0.1:%s ' % self.port
		self.socketIOServer = SocketIOServer(('', self.port), self.app, resource="socket.io")
		self.app.add_url_rule("/socket.io/<path:remaining>","socketio",self.socketio)		

	def start(self):
		self.socketIOServer.serve_forever()

	def authenticate(self,connection, auth_params):
		if not auth_params.has_key("id"):
			return connection.authentication_reply(0, 0, "Invalid Id")

		connection.authentication_reply(1, auth_params["id"], "Done")
		self.new_connection(connection, auth_params["id"])

	def new_connection(self,connection, id):
		logging.debug("Transport:Connected")
		self._emit("connection", id, 0, connection)

	def disconnect_connection(self, connection):
		self._emit("disconnect", connection.id, 0, connection)
	
	def socketio(self,remaining):	
		try:			
			print request
			socketio_manage(request.environ, {'/relay': PersistentConnection}, self)
		except:
			self.app.logger.error("Exception while handling socketio connection",exc_info=True)
		return Response()


class PersistentConnection(BaseNamespace, Events):

	
	def initialize(self):
		self._connection_manager = self.request		
		self._is_authenticated=False
		self.id = 0

		self.logger = logging
		self.log("Socketio session started")

	def log(self, message):
		self.logger.debug("PersistentConnection : [{0}] {1}".format(self.socket.sessid, message))
	
	def recv_connect(self):    	
		self.log("Connected")    	
		

	def recv_disconnect(self):    	
		self.log('Disconnected')
		self._connection_manager.disconnect_connection(self)
		self.disconnect(silent=True)
		return True

	def on_authenticate(self, auth_params):
		self._connection_manager.authenticate(self, auth_params)
		
	def authentication_reply(self, code, id, message):
		if code is 1:
			self._is_authenticated = True
			self.id = id

		self._emit("authenticated", {"code":code, "message":message})

	def on_message(self, msg):    	
		if not self._is_authenticated:
			self.send_message("Not Authenticated")

		self.log('incoming message {0}'.format(msg))    	
		self._emit("message", msg)

	def send_message(self, message):
		self.log('sending message {0}'.format(message))    	
		self.emit("message",message)

	def start(self):
		pass

if __name__ == '__main__':
	
	pt =  PersistentTransport()
	pt.start()
