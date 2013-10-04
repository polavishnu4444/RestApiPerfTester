
from ..relay import RelayServer
from ..qtransport import QueueTransport

from ..persistence import PersistentTransport


def start_relay():
	relayserver = RelayServer()
	q_transport = QueueTransport()
	relayserver.add_transport(q_transport)
	persistent_transport = PersistentTransport()
	relayserver.add_transport(persistent_transport)
	relayserver.start()


if __name__ == "__main__":
    start_relay()