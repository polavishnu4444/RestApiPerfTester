import gevent

class Events(object):
    def __init__(self):             
        self.registeredCallbacks = {}

    def on(self, eventName, callback):        
        # print "\n=================================="
        # print "on",self, eventName, callback
        events = self.registeredCallbacks.setdefault(eventName, []);
        self.registeredCallbacks[eventName].append(callback);

        # print "total events",self, [ p for p in self.registeredCallbacks.iteritems()]
        # print "\n=================================="

    def _emit(self, eventName, *args, **kwargs):        
        callbacks = self.registeredCallbacks.get(eventName)
        # print "emitting", eventName, callbacks
        if not callbacks:
            return;
        # print "calling something", eventName
        firedCallbacks  = [gevent.spawn(callback, *args, **kwargs) for callback in callbacks]
        gevent.sleep(0)
