from haigha.connection import Connection
from haigha.message import Message
import gevent
import gevent.event as gevent_event
import logging
import json

logging.basicConfig(level=logging.DEBUG)

#gevent.monkey_patch_all()

class App(object):
	def __init__(self, serverName, **options):
		self.serverName = serverName
		self._routes = {}
		self.options = options
		self.version = self.options.get("version", "0.1")

		self.queueName = "{0}/{1}/request".format(self.serverName, self.version)
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

	def get_route(self,operation):		
		return self._routes.get(operation,None)

	def _process_message(self,message):
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

		print " getting msg", message
		body = str(message.body).encode('string_escape')
		if not body:
			pass

		body=json.loads(body)
		context = body["context"] or None
		if not context:
			logging.debug("QueueServer:Received invalid message: No context: {0}".format(message))		
			return 

		operation = context.get("operation",None)
		print "\nOperation is ", operation
		if not operation:
			pass

		func = self.get_route(operation);
		if(not func):
			pass

		reply_to = message.properties.get("reply_to",None)

		if not reply_to:
			return 
			

		self._pending_requests[context["cid"]] = context
		self._pending_requests[context["cid"]]["reply_to"]=reply_to

		ret = func({
			"context": context,
			"content": body["content"]
			})
		# print "message properties ", message.properties


		# self.send_reply(reply_to, ret)

	def send_reply(self, message):
		'''
		message shoud be :
		{
			context:{
				reply_to_cid:<unique id>
			},
			content:<content>
		}
		'''
		reply_to_cid = message["reply_to_cid"] or None
		if not reply_to_cid:			
			return

		reply_context = self._pending_requests[reply_to_cid] or None
		if not reply_context:
			logging.error("No pending request for cid", reply_to_cid)
			return

		self.send_reply(reply_context["reply_to"], {
				"context":reply_context,
				"content":message["content"]
			})


	def _send_reply(self, reply_key, ret):
		msg = Message(ret)
		self._channel.basic.publish(msg, self.exchange, reply_key)

	def _message_pump_greenthread(self):
	    print "Entering Message Pump"
	    try:
	      while self.running:
	        # Pump
	        self._connection.read_frames()
	        
	        # Yield to other greenlets so they don't starve
	        gevent.sleep()
	    except Exception as e:
	    	print e
	    finally:
	      print "Leaving Message Pump", self.running
	      #self._done_cb()
	    return



	def start(self):
		self._connection = Connection(
			transport='gevent',
  			user='guest', password='guest',
  			vhost=self.vhost, host=self.queueServer,
  			heartbeat=None, debug=True)
		self._channel = self._connection.channel()
		self._channel.add_close_listener(self._channel_closed_cb)
    	
	    # Create and configure message exchange and queue
		print self.exchange
		print self.queueName

		self._channel.exchange.declare(self.exchange, 'topic')
		self._channel.queue.declare(self.queueName, auto_delete=False)
		self._channel.queue.bind(self.queueName, self.exchange, self.queueName)
		self._channel.basic.consume(queue=self.queueName,
		                            consumer=self._process_message)
		# Start message pump
		self.running = True
		self._message_pump_greenlet = gevent.spawn(self._message_pump_greenthread)
		print "Started"

	def stop(self):
		self.running = False


	def _channel_closed_cb(*args):
		print "Channel Closed", args

if __name__ == "__main__":	
	app = App("MyServer")

	@app.route("get")
	def get(request):
		print "\n Got Request",request
		return "ok"
    
	@app.route("put")
	def put(request):
		print "\n Got Request",request
		return "ok"

	app.start()
	#raw_input();
	
	gevent.sleep(15000)
	print "Done!"
	
