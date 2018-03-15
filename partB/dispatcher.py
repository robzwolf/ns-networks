try:
    import queue
except ImportError:
    import Queue as queue
import Pyro4
from Pyro4.util import SerializerBase
from work_item import WorkItem

# For 'work_item.Work_Item' we register a deserialisation hook to be able to get these back from Pyro
SerializerBase.register_dict_to_class("work_item.WorkItem", WorkItem.from_dict)


@Pyro4.expose
@Pyro4.behavior(instance_mode="single")
class DispatcherQueue():
    def __init__(self):
        self.work_queue = queue.Queue()
        self.result_queue = queue.Queue()

    def put_work(self, item):
        self.work_queue.put(item)

    def get_work(self, timeout=5):
        try:
            return self.work_queue.get(block=True, timeout=timeout)
        except queue.Empty:
            raise ValueError("No result available")

    def put_result(self, item):
        self.result_queue.put(item)

    def get_result(self, timeout=5):
        try:
            return self.result_queue.get(block=True, timeout=timeout)
        except queue.Empty:
            raise ValueError("No result available")

    def work_queue_size(self):
        return self.work_queue.qsize()

    def result_queue_size(self):
        return self.result_queue.qsize()


# Main program
Pyro4.Daemon.serveSimple({
    DispatcherQueue: "distributed_ftp.dispatcher"
})
print("Dispatcher running")
