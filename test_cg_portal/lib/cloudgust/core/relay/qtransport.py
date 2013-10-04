import re
import unicodedata
from gevent import monkey
from socketio.server import SocketIOServer
from relay import RelayTransport
from ..events import Events
import logging
from ..queues.QueueServerBase import App

logging.basicConfig(level=logging.DEBUG)

monkey.patch_all()

class QueueTransport(RelayTransport):
	def __init__(self):
		super(QueueTransport, self).__init__()		
		self.server_name = "relayserver"
		self._initialize()

	def _initialize(self):
		self._connections={}
		self.queueClient = App(self.server_name)
		self.queueClient.add_route("get", self.receive_message)

	def start(self):
		self.queueClient.start()

	def authenticate(self,connection, auth_params):
		if not auth_params.has_key("id"):
			return connection.authentication_reply(0, 0, "Invalid Id")

		connection.authentication_reply(1, auth_params["id"], "Done")
		self.new_connection(connection, auth_params["id"])

	def disconnect_connection(self, connection):
		self._emit("disconnect", connection.id, 0, connection)

		
	def receive_message(self, message):
		#receive message from queue and send to relay port
		'''
		message : 
		{
			context:{
				target:<id>,
				cid:<unique id>
			},
			content:<content>
		}
		'''
		context = message["context"] or None
		if not context:
			logging.debug("QueueTransport: Received invalid message: No context {0}".format(message))		
			return 

		target_id = context["target"] or None
		if not target_id:
			logging.error("QueueTransport:Invalid message received: No target: {0}".format(message))
			return

		logging.debug("QueueTransport: receive_message: [{0}]/{1}".format(target_id, message))		
		connection = self._get_connection(target_id)
		connection.on_message({
				"context":{
					"cid":context["cid"]
				},
				"content":message["content"]
			})

		
		
	def send_message(self, id, message):
		#send message to queue 
		'''
		message shoud be :
		{
			context:{
				reply_to_cid:<unique id>
			},
			content:<content>
		}
		'''
		logging.debug("QueueTransport: send_message: [{0}]/{1}".format(id, message))
		self.queueClient.send_reply(message)
		pass

	def _get_connection(self, target_id):
		if target_id not in self._connections:
			conn =  QueueConnection(self, target_id)
			conn.initialize()
			self._new_connection(target_id, conn)		
		return self._connections[target_id]

	
	def _new_connection(self,id, connection):
		logging.debug("Transport:Connected")
		self._connections[id]=connection
		self._emit("connection", id, 1, connection)



class QueueConnection(Events):

	def __init__(self, qtransport_manager, id):
		super(QueueConnection, self).__init__()
		self.id = id
		self._q_manager = qtransport_manager

	def initialize(self):
		self.logger = logging

	def log(self, message):
		self.logger.debug("QueueConnection : [{0}] {1}".format(self.id, message))

	def on_message(self, msg):    	
		self.log('incoming message {0}'.format(msg))    	
		self._emit("message", msg)

	def send_message(self, message):
		print "here"
		self.log('sending message {0}'.format(message))    	
		self._q_manager.send_message(self.id, message)

	def start(self):
		pass

