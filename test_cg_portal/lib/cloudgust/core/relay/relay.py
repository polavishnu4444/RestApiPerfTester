from ..events import Events
import gevent
from gevent import monkey
import logging

monkey.patch_all()

logging.basicConfig(level=logging.DEBUG)

class RelayServer(object):

	def __init__(self):
		self._started = False
		self._transports=[]
		self._relay_connections={}
		self._relayEPs = {}

	@property
	def started(self):
		return self._started

	@started.setter
	def started(self, value):
		self._started = value

	def add_transport(self, transport):
		self._add_transport(transport)
		self._bind_transport(transport)

	def _add_transport(self, transport):
		self._transports.append(transport)		

	def _bind_transport(self, transport):
		transport.on("connection", self._new_connection);
		transport.on("disconnect", self._disconnect)		

	def _new_connection(self,id, direction, connection):
		if not self.started:
			logging.error("Not Started")
			return		

		relayEP = self._get_relayep(id, direction)
		logging.debug("Relay:Connected %s", relayEP)
		relay_connection = RelayConnection(relayEP, connection, id, direction)
		self._add_relay_connection(id, direction, relay_connection)
		relay_connection.start()
		gevent.sleep(0)

	def _add_relay_connection(self, id, direction, relay_connection):
		conn = self._relay_connections.get(id, {})
		conn[direction]=relay_connection
		self._relay_connections[id]=conn

	def _disconnect(self,id, direction, connection):
		conns = self._relay_connections.get(id, {})
		conn = conns.get(direction)

		if conn and conn == connection:
			del conns[direction]
		else:
			raise Exception("Invalid disconnect request. Connection does not exist")		
		

	def _get_relayep(self, id, direction):	
		# print "\n\n All Relay EPS:", [p for p in self._relayEPs.iteritems()]
		cleaned_id = str(id).lower()
		relayEps = self._relayEPs.get(cleaned_id) or RelayEPPair(id)
		self._relayEPs[cleaned_id]=relayEps
		# print "\n\n All Relay EPS finally:", [p for p in self._relayEPs.iteritems()]
		return relayEps._endpoints[direction]

	def start(self):
		self._start_transports()
		self.started = True
		gevent.sleep(120)

	def stop(sekf):
		self.started = False


	def _start_transports(self):
		for t in self._transports:
			gevent.spawn(t.start)
		

class RelayConnection(object):
	def __init__(self, relayEP, transport_connection, id, direction):
		self.id = id
		self.direction = direction
		self.relayEP = relayEP
		self.connection=transport_connection

	def start(self):
		logging.debug("starting connection for %s", self.relayEP)
		self.connection.on("message", self.relayEP.send_in)		
		self.relayEP.on("message", self.connection.send_message)

		self.relayEP.start()
		self.connection.start()

class RelayEPPair:
	def __init__(self, id):
		self.id=id
		self._endpoints = [RelayEP(id, 0), RelayEP(id,1)]
		self._connect_endpoints()

	def _connect_endpoints(self):
		self._endpoints[0].on("send_in", self._endpoints[1].send_out)
		self._endpoints[1].on("send_in", self._endpoints[0].send_out)


class RelayEP(Events):
	def __init__(self, id, direction):
		self.id= id
		self.direction = direction	
		super(RelayEP, self).__init__()

	def start(self):
		#start consuming messages from the request queue
		pass

	def send_in(self,message):
		logging.debug("RelayEP %s received send in  %s" ,self, message)
		self._emit("send_in", message )		
		
	def send_out(self, message):
		logging.debug("RelayEP %s received send out  %s" ,self,  message)
		self._emit("message", message )	

	def __str__(self):
		return "{0}|{1}".format(self.id, self.direction)

class RelayTransport(Events):
	def __init__(self):
		super(RelayTransport, self).__init__()

	def _connected(self, id, direction, connection):
		logging.debug("Connected event firing")
		self._emit("connection", id, direction, connection)

	def _disconnect(self, connection):
		self._emit("disconnect", id, direction, connection)

class RelayTransportConnection(Events):
	def __init__(self):
		super(RelayTransportConnection, self).__init__()	

	def send_message(self, message):		
		logging.debug("ReplayTransportConnection received message from inside: %s", message )

	def _message_received(self, message):
		logging.debug("RelayTransportConnection received %s", message)
		self._emit("message", message)

	def start(self):
		pass

if __name__ == "__main__":
	print globals()

	logging.basicConfig(level=logging.DEBUG)

	server = RelayServer()
	transport = RelayTransport()
	server.add_transport(transport)
	server.start()

	connection0 = RelayTransportConnection()
	transport._connected("0",0,connection0)

	connection1 = RelayTransportConnection()
	transport._connected("0",1,connection1)

	connection0._message_received({"a":10})

	gevent.sleep(2)