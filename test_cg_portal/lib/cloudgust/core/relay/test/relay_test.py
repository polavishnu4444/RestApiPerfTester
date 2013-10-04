
from ..relay import RelayServer
from ..persistence import PersistentTransport


def start_relay():
	relayserver = RelayServer()
	persistent_transport = PersistentTransport()

	relayserver.add_transport(persistent_transport)

	relayserver.start()


if __name__ == "__main__":
	start_relay()