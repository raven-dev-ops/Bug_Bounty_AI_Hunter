from .base import Connector


CONNECTORS = {}


def register(connector):
    if not isinstance(connector, Connector):
        raise ValueError("Connector must inherit from Connector.")
    CONNECTORS[connector.name] = connector


def get_connector(name):
    return CONNECTORS.get(name)
