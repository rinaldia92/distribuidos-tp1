from common.client import Client

class Middleware:
    def __init__(self, conn):
        self.conn = conn

    def receive_message(self):
        msg = ''
        character = ''
        while character != '\n':
            character = self.conn.recv(1).decode('utf-8')
            msg = msg + character
        return msg

    def resend_message(self, host, port, message):
        client = Client(self.host, self.port)
        client.send_message(message)
        client.close()

    def respond_message(self, message):
        self.conn.sendall(message.encode('utf-8'))