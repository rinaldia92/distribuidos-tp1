import time
import logging
import json
import uuid
from common.client import Client
from common.utils import download, save_to_file, grep_folders, grep_file, repos_garbage_collector

def monitor(new_repos_queue, repos_search_queue, cron_time):
	time.sleep(cron_time)
	logging.info("New repositories to be available: {}".format(new_repos_queue.qsize()))
	logging.info("Pending queries: {}".format(repos_search_queue.qsize()))

def garbage_collector(folder, file, cron_time, lock):
	time.sleep(cron_time)
	repos_garbage_collector(folder, file, lock)

def query_controller(server_request, repos_search_queue, repo_file, lock):
	conn, addr = server_request.accept_new_connection()
	message = server_request.receive_message(conn)
	params = json.loads(message)
	repos = grep_file(repo_file, params["regex_repos"], lock)
	data = {
		"thread_id": params["thread_id"],
		"regex": params["regex"],
		"paths": repos
	}
	repos_search_queue.put(data)

def grep_files_controller(host, port, repos_search_queue, folder):
	params = repos_search_queue.get()
	results = grep_folders(params["regex"], params["paths"], folder)
	message = {
		"thread_id": params["thread_id"],
		"message": len(results)
	}
	try:
		client_response = Client(host, port)
		client_response.send_message(json.dumps(message))
		client_response.close()
		for res in results:
			message["message"] = res
			client_response = Client(host, port)
			client_response.send_message(json.dumps(message))
			client_response.close()	
	except ConnectionRefusedError:
		logging.error("Connection refused. Can't return grep results")
		raise

def download_controller(server_download, new_repos_queue):
	conn, addr = server_download.accept_new_connection()
	message = server_download.receive_message(conn)
	params = json.loads(message)
	branch = params["branch"]
	name = params["url"].split('/')[-1][:-4]
	uid = str(uuid.uuid4())
	complete_name = "{}-{}-{}".format(uid, name, branch)
	try:
		download(params["url"], params["branch"], "./repositories/{}".format(complete_name))
	except Exception:
		logging.error("Unable to download repository {}".format(params["url"]))
		return
	register = { "name": name, "branch": branch, "complete_name": complete_name }
	new_repos_queue.put(register)

def update_repositories_controller(file, new_repos_queue, lock):
	register = new_repos_queue.get()
	save_to_file(file, register, lock)

def monitor_threads_controller(threads):
	kill_threads = False
	for thread in threads:
		if not thread.alive():
			kill_threads = True
			break
	if kill_threads:
		for thread in threads:
			thread.stop()
	return kill_threads