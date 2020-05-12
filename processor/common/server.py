import socket
import logging

class Server:
    def __init__(self, port, listen_backlog):
        # Initialize server socket
        self._server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server_socket.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server_socket.bind(('', port))
        self._server_socket.listen(listen_backlog)

    def send_message(self, conn, message):
        """
        Sending message to server
        """
        logging.info('Sending message')
        conn.sendall(message.encode('utf-8'))


    def receive_message(self, conn):
        return conn.recv(1000).decode('utf-8').rstrip()

    def close(self):
        self._server_socket.close()



    def accept_new_connection(self):
        """
        Accept new connections

        Function blocks until a connection to a client is made.
        Then connection created is printed and returned
        """

        # Connection arrived
        logging.info("Proceed to accept new connections")
        c, addr = self._server_socket.accept()
        logging.info('Got connection from {}'.format(addr))
        return c, addr