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
        message_to_send = message + '\n'
        self._client_socket.sendall(message_to_send.encode('utf-8'))


    def receive_message(self):
        msg = ''
        character = ''
        while character != '\n':
            msg = msg + character
            character = self._client_socket.recv(1).decode('utf-8')
        return msg

    def close(self):
        self._client_socket.close()
