import os
import subprocess
import json

def download(repository, branch, destination):
    p = subprocess.Popen(["git", "clone", repository, "-b", branch, destination], stdout= subprocess.PIPE, stderr = subprocess.PIPE)
    proc_out, proc_err = p.communicate()

def grep_folders(regex, paths, folder):
    results = []
    procs_list = []
    for path in paths:
        p = subprocess.Popen(['grep', '-rl', regex, "{}{}".format(folder, path)], stdout= subprocess.PIPE)
        procs_list.append(p)
    for proc in procs_list:
        proc_out, proc_err = proc.communicate()
        hosts_splitted = proc_out.decode("utf-8").split('\n')
        hosts_splitted.pop()
        results = results + hosts_splitted
    return results

def save_to_file(filename, register, lock):
    lock.write_acquire()
    json_file = []
    try:
        with open(filename, 'r') as file:
            json_file = json.load(file)
            for element in json_file:
                if element["name"] == register["name"] and element["branch"] == register["branch"]:
                    if  element["status"] == 'actual':
                        element["status"] = 'old'
                    elif element["status"] == 'old':
                        element["status"] = 'older'
    except FileNotFoundError as fileError:
        pass
    json_file.append({ "name": register["name"], "branch": register["branch"], "complete_name": register["complete_name"], "status": "actual" })
    with open(filename, 'w') as file:
        json.dump(json_file, file)
    lock.write_release()


def grep_file(file, regex, lock):
    lock.read_acquire()
    p = subprocess.Popen(["jq", ".[] | select(.name | test(\"{}\")) | select(.status | test(\"actual\")) | .complete_name".format(regex) , file], stdout= subprocess.PIPE, stderr = subprocess.PIPE)
    proc_out, proc_err = p.communicate()
    lock.read_release()
    if len (proc_err.decode('utf-8')) > 0:
        return []
    repos = proc_out.decode("utf-8").split('\n')[:-1]
    repos = list(map(lambda repo: repo.strip('\"'), repos)) 
    return repos

def repos_garbage_collector(folder, filename, lock):
    lock.write_acquire()
    repos_to_remove = []
    actual_repos = []
    procs_list = []
    try: 
        with open(filename, 'r') as file:
            json_file = json.load(file)
            for repo in json_file:
                if repo["status"] == 'oldest':
                    repos_to_remove.append(repo["complete_name"])
                else:
                    actual_repos.append(repo)
    except FileNotFoundError as fileError:
        return
    for repo in repos_to_remove:
        p = subprocess.Popen(['rm', '-r', "{}{}".format(folder, repo)], stdout= subprocess.PIPE, stderr = subprocess.PIPE)
        procs_list.append(p)
    for proc in procs_list:
        proc_out, proc_err = proc.communicate()
    with open(filename, 'w') as file:
        json.dump(actual_repos, file)
    lock.write_release()

    