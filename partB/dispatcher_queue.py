from job import Job


class DispatcherQueue:
    def __init__(self):
        self.job_queue = []

    def __str__(self):
        return "<DispatcherQueue, job_queue_size()={}>".format(self.job_queue_size())

    def put_job(self, job):
        """
        Puts a job on the queue.
        """
        self.job_queue.append(job)

    def get_job(self):
        """
        Gets the most recent job from the queue.
        """
        if self.job_queue_size() > 0:
            job_dict = self.job_queue[0]
            del self.job_queue[0]
            job = Job.from_dict("job.Job", job_dict)
            return job
        raise ValueError("No result available")

    def job_queue_size(self):
        """
        Returns the size of the job queue.
        """
        return len(self.job_queue)

    @staticmethod
    def from_dict(class_name, dq_dict):
        """
        Deserialises a DispatcherQueue from Pyro4.
        """
        assert class_name == "dispatcher_queue.DispatcherQueue"
        dq = DispatcherQueue()
        dq.job_queue = dq_dict["job_queue"]
        return dq
