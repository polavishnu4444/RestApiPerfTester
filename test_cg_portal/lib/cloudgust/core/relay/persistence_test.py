__author__ = 'CloudGust-Laptop1'

from time import sleep
from socketio_client_gevent import SocketIO, BaseNamespace
from socketio_client_gevent import SocketIOConnectionError
import gevent
from gevent import monkey


monkey.patch_all()

class ChatNamespace(BaseNamespace):

    def on_message(self, *args):
        print 'on_aaa_response', args
        

def connect_relay_server( server,port):
        server_details = server
        try:
            if len(server_details) > 1:
                socket = SocketIO(server_details, int(port))
            else:
                socket = SocketIO(server_details[0], 80)
            isConnected = True

            requestNamespace = socket.define(ChatNamespace,"/relay")
            requestNamespace.emit("authenticate",{"id":"1"})
            requestNamespace.emit("message",{"rohit":"name"})
            socket.wait(seconds=60)
            socket.disconnect()
            gevent.sleep(1)
        except Exception as e:
            isConnected = False
            print e

connect_relay_server("localhost",5000)


