# try:
#     import queue
# except ImportError:
#     import Queue as queue
from time import time


class DispatcherQueue:
    def __init__(self):
        # self.job_queue = queue.Queue()
        # self.result_queue = queue.Queue()
        self.job_queue = []
        self.result_queue = []

    def __str__(self):
        return "<DispatcherQueue, job_queue_size()={}, result_queue_size()={}>".format(self.job_queue_size(),
                                                                                       self.result_queue_size())

    def put_job(self, job):
        # self.job_queue.put(item)
        self.job_queue.append(job)
        print(self.job_queue_size())

    def get_job(self):
        # try:
        #     return self.job_queue.get(block=True, timeout=timeout)
        # except queue.Empty:
        #     raise ValueError("No result available")
        # start_time = time()
        # while time() < start_time + timeout:
        if self.job_queue_size() > 0:
            job = self.job_queue[0]
            del self.job_queue[0]
            print("Found job={}".format(job))
            return job
        raise ValueError("No result available")

    def put_result(self, result):
        # self.result_queue.put(job)
        self.result_queue.append(result)

    def get_result(self, timeout=5):
        # try:
        #     return self.result_queue.get(block=True, timeout=timeout)
        # except queue.Empty:
        #     raise ValueError("No result available")
        result = self.result_queue[0]
        del self.result_queue[0]
        return result

    def job_queue_size(self):
        # return self.job_queue.qsize()
        return len(self.job_queue)

    def result_queue_size(self):
        # return self.result_queue.qsize()
        return len(self.result_queue)

    @staticmethod
    def from_dict(class_name, dq_dict):
        """
        Deserialise a DispatcherQueue from Pyro4
        """
        assert class_name == "dispatcher_queue.DispatcherQueue"
        # j = Job(j_dict["command"], j_dict["data"])
        # # j = Job(j_dict["item_id"], j_dict["data"])
        # j.result = j_dict["result"]
        # j.processed_by = j_dict["processed_by"]
        # return j
        print("from_dict called. dq_dict = {}".format(dq_dict))
        dq = DispatcherQueue()
        dq.job_queue = dq_dict["job_queue"]
        dq.result_queue = dq_dict["result_queue"]
        return dq
