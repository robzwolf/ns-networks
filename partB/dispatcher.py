# try:
#     import queue
# except ImportError:
#     import Queue as queue
from time import time

import Pyro4
from Pyro4.util import SerializerBase
from job import Job
from dispatcher_queue import DispatcherQueue

# For 'job.Job' we register a deserialisation hook to be able to get these back from Pyro
SerializerBase.register_dict_to_class("job.Job", Job.from_dict)

# For 'dispatcher_queue.DispatcherQueue' we register a deserialisation hook to be able to get these back from Pyro
SerializerBase.register_dict_to_class("dispatcher_queue.DispatcherQueue", DispatcherQueue.from_dict)

@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Dispatcher:
    def __init__(self):
        self.server_queues = {}

    def register_server(self, server_name):
        print("Server {} registered itself.".format(server_name))
        dq = DispatcherQueue()
        self.server_queues[server_name] = dq

    def get_server_queue(self, server_name, timeout=5):
        start_time = time()
        while time() < start_time + 5:
            sq = self.server_queues[server_name]
            if sq.job_queue_size() > 0:
                # print("Called get_server_queue({})".format(server_name))
                print("sq from get_server_queue({}) = {}".format(server_name, sq))
                return sq
        raise ValueError("Server queue has no jobs in it")
        # return

    # def get_server_queues(self):
    #     return self.server_queues

    def get_hello(self):
        return "Hello"

    def put_job(self, job):
        print("Got job = {}".format(job))
        for sn in self.server_queues.keys():
            self.server_queues[sn].put_job(job)
            print("Put job={} into queue with name '{}'".format(job, sn))

    def get_result(self):
        print("Client requested result")
        return None


# Main program
Pyro4.Daemon.serveSimple({
    Dispatcher: "distributed_ftp.dispatcher"
})
print("Dispatcher running")
