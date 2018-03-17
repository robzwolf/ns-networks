try:
    import queue
except ImportError:
    import Queue as queue
import Pyro4
from Pyro4.util import SerializerBase
from job import Job

# For 'job.Job' we register a deserialisation hook to be able to get these back from Pyro
SerializerBase.register_dict_to_class("job.Job", Job.from_dict)


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class Dispatcher():
    def __init__(self):
        self.job_queue = queue.Queue()
        self.result_queue = queue.Queue()

    def put_job(self, item):
        self.job_queue.put(item)
        print(self.job_queue_size())

    def get_job(self, timeout=5):
        try:
            return self.job_queue.get(block=True, timeout=timeout)
        except queue.Empty:
            raise ValueError("No result available")

    def put_result(self, item):
        self.result_queue.put(item)

    def get_result(self, timeout=5):
        try:
            return self.result_queue.get(block=True, timeout=timeout)
        except queue.Empty:
            raise ValueError("No result available")

    def job_queue_size(self):
        return self.job_queue.qsize()

    def result_queue_size(self):
        return self.result_queue.qsize()


# Main program
Pyro4.Daemon.serveSimple({
    Dispatcher: "distributed_ftp.dispatcher"
})
print("Dispatcher running")
