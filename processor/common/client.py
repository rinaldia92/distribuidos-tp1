import socket
import logging

class Client:
    def __init__(self, host, port):
        # Initialize server socket
        self._client_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._client_socket.connect((host, port))

    def send_message(self, message):
        """
        Sending message to server
        """
        logging.info('Sending message')
        self._client_socket.sendall(message.encode('utf-8'))


    def receive_message(self):
        msg = ''
        character = ''
        while character != '\n':
            character = self._client_socket.recv(1).decode('utf-8')
            msg = msg + character
        return msg

    def close(self):
        self._client_socket.close()
