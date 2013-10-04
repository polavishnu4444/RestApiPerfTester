from haigha.connection import Connection
from haigha.message import Message
import gevent
import gevent.event as gevent_event
import json
import logging


logging.basicConfig(level=logging.DEBUG)

#gevent.monkey_patch_all()

class AppClient(object):
	def __init__(self, serverName, **options):
		self.serverName = serverName
		self._routes = {}
		self.options = options
		self.version = self.options.get("version", "0.1")

		self.queueName = "{0}/{1}/request".format(self.serverName, self.version)
		self.reply_queue_name = "{0}/{1}/reply".format(self.serverName, self.version)
		self.exchange=self.options.get("exchange","main")
		self.vhost = self.options.get("vhost", "/")
		self.queueServer = self.options.get("queueServer","localhost")
		self._pending_requests = {}

	def route(self,operation):		
		def wrap(func):
			self.add_route(operation, func)
			return func
		return wrap

	def add_route(self,operation, func):		
		self._routes[operation]=func

	def _process_reply(self, message):
		'''
			Receives message.body containing following attributes
			{				
				context:
				{
					operation:<operation>,
					params:<params>,
					cid:<id for the request>
				},
				content:<content>
			}
		'''
		logging.debug(" Reply: Getting msg: {0}".format(message))

		body = str(message.body).encode('string_escape')
		if not body:
			pass

		body=json.loads(body)

		context = body["context"] or None
		if not context:
			logging.debug("QueueServer:Received invalid message: No context: {0}".format(message))		
			return 

		cid = context["cid"]

		callback = self._pending_requests[cid]
		if not callback:
			logging.error("No callback registered for cid:",cid)
			return 

		gevent.spawn(callback, body["content"])
		gevent.sleep(0)	

	def send(self, message, options, callback):
		
		context = options or {}

		context["operation"]="get"
		context["cid"]=1

		self._pending_requests[context["cid"]]=callback

		message = Message(json.dumps({
			"context": context,
			"content" : message
			}),None, reply_to=self.reply_queue_name)

		logging.debug("Sending message to {0}|{1}".format(self.exchange,self.queueName, message))
		self._channel.basic.publish( message, self.exchange,self.queueName)

		gevent.sleep(0)
		

	def start(self):
		self._connection = Connection(
			transport='gevent',
  			user='guest', password='guest',
  			vhost=self.vhost, host=self.queueServer,
  			heartbeat=None, debug=True)
		self._channel = self._connection.channel()
		self._channel.add_close_listener(self._channel_closed_cb)
    	
	    # Create and configure message exchange and queue
		self._channel.exchange.declare(self.exchange, 'topic')
		self._channel.queue.declare(self.queueName, auto_delete=False)		
		self._channel.queue.declare(self.reply_queue_name, auto_delete=False)

		print "reply q name", self.reply_queue_name
		self._channel.queue.bind(self.reply_queue_name, self.exchange, self.reply_queue_name)
		# self._channel.basic.consume(queue=self.reply_queue_name,
		#                             consumer=self._process_reply)

		# Start message pump
		self.running = True
		gevent.spawn(self._message_pump_greenthread)
		print "Started"
		gevent.sleep(0)
		

	def _message_pump_greenthread(self):
	    logging.debug("Entering Message Pump")
	    try:
	      while self.running:
	        # Pump
	        self._connection.read_frames()
	        
	        # Yield to other greenlets so they don't starve
	        gevent.sleep()
	    except Exception as e:
	    	print e
	    finally:
	      logging.debug("Leaving Message Pump, {0}".format(self.running))	      
	    return


	def stop(self):
		self.running = False


	def _channel_closed_cb(self,*args):
		print "Channel Closed"

if __name__ == "__main__":	
	app = AppClient("relayserver")

	def callback(message):
		print "Received Reply:", message

	app.start()
	app.send({"name":"fromQueueClient 123"},{"target":1}, callback)

	gevent.sleep(120)

	
	
