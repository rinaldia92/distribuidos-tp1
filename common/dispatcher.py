from common.client import Client

class Dispatcher:

    def send_message(self, host, port, message):
        client = Client(host, port)
        client.send_message(message)
        client.close()    