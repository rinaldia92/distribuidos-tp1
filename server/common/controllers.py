import logging
import json
from common.client import Client

def download_controller(server_downloads, host, port):
	while True:
		conn, addr = server_downloads.accept_new_connection()
		message = server_downloads.receive_message(conn)
		message_to_client = "Download request received"
		logging.info(message_to_client)
		try:
			client_downloads = Client(host, port)
			client_downloads.send_message(message)
			client_downloads.close()
		except ConnectionRefusedError:
			message_to_client = "Download request fail"
		server_downloads.send_message(conn, message_to_client)

def query_controller(server_query, host, port, response_queue, thread_id):
	while True:
		conn, addr = server_query.accept_new_connection()
		msg = server_query.receive_message(conn)
		data = json.loads(msg)
		data["thread_id"] = thread_id
		results = []
		message_to_client = ''
		try:
			client_query = Client(host, port)
			client_query.send_message(json.dumps(data))
			client_query.close()
			amount = response_queue.get()
			for _ in range(int(amount)):
				file = response_queue.get() 
				results.append(file)
			logging.info(results)
			message_to_client = str(results)
		except ConnectionRefusedError:
			message_to_client = 'Query request fail'
		server_query.send_message(conn, message_to_client)

def grep_results_controller(server_responses, response_queues):
	while True:
		conn_resp, addr_resp = server_responses.accept_new_connection()
		response = server_responses.receive_message(conn_resp)
		response = json.loads(response)
		queue_index = int(response["thread_id"])
		msg = response["message"]
		response_queues[queue_index].put(msg)
		