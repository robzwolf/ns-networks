import copy
from time import time
import Pyro4
from Pyro4.util import SerializerBase
from job import Job
from dispatcher_queue import DispatcherQueue

# For "job.Job" we register a deserialisation hook to be able to get these back from Pyro
SerializerBase.register_dict_to_class("job.Job", Job.from_dict)

# For "dispatcher_queue.DispatcherQueue" we register a deserialisation hook to be able to get these back from Pyro
SerializerBase.register_dict_to_class("dispatcher_queue.DispatcherQueue", DispatcherQueue.from_dict)


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Dispatcher:
    def __init__(self):
        self.server_queues = {}
        self.result_queue = []

    def register_server(self, server_name):
        if server_name not in self.server_queues.keys():
            print("Server '{}' registered itself.".format(server_name))
            dq = DispatcherQueue()
            self.server_queues[server_name] = dq
        else:
            print("Server '{}' re-registered itself.".format(server_name))

    def get_server_queue(self, server_name, timeout=5):
        start_time = time()
        while time() < start_time + timeout:
            sq = self.server_queues[server_name]
            if sq.job_queue_size() > 0:
                print("sq from get_server_queue({}) = {}".format(server_name, sq))
                returnable_sq = copy.deepcopy(sq)
                del sq.job_queue[0]
                return returnable_sq
        raise ValueError("Server queue has no jobs in it")

    def get_hello(self):
        return "Hello"

    def put_job(self, job):
        print("Got job = {}".format(job))

        # Handle the job, depending on its command
        if job.command == "UPLD_INIT":
            pass
        elif job.command == "UPLD_DATA":
            pass
        elif job.command == "DWLD":
            pass
        elif job.command == "DELF_INIT":
            pass
        elif job.command == "DELF_CONF":
            pass
        elif job.command == "LIST":
            pass
        else:
            print("Unrecognised command: {}".format(job.command))
            return

        for sn in self.server_queues.keys():
            self.server_queues[sn].put_job(job)
            print("Put job={} into queue with name '{}'".format(job, sn))

    def put_result(self, job_result):
        print("Server '{}' put result '{}' in results_queue".format(job_result.processed_by, job_result.result))
        self.result_queue.append(job_result)

    def get_result(self):
        print("Client requested result")
        while True:
            if len(self.result_queue) > 0:
                result = copy.deepcopy(self.result_queue[0])
                print("Result is '{}'".format(result))
                del self.result_queue[0]
                return result


# Main program
Pyro4.Daemon.serveSimple({
    Dispatcher: "distributed_ftp.dispatcher"
})
print("Dispatcher running")
