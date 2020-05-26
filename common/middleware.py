from common.client import Client

class Middleware:
    def __init__(self, conn):
        self.conn = conn

    def receive_message(self):
        msg = ''
        character = ''
        while character != '\n':
            msg = msg + character
            character = self.conn.recv(1).decode('utf-8')
        return msg

    def respond_message(self, message):
        message_to_send = message + '\n'
        self.conn.sendall(message_to_send.encode('utf-8'))