from common.client import Client

class Dispatcher:
    def __init__(self, host, port):
        self.host = host
        self.port = port

    def send_message(self, message):
        client = Client(self.host, self.port)
        client.send_message(message)
        client.close()    