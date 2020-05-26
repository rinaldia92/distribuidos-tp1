class ProcessController:
    def __init__(self, processes):
        self.processes = processes
    
    def monitor(self):
        kill_processes = False
        for process in self.processes:
            if not process.alive():
                kill_processes = True
                break
        if kill_processes:
            for process in processes:
                process.stop()
        return kill_processes
