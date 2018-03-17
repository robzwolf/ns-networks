class Job():
    def __init__(self, command, data=None):
        # print("Created Job, cmd={}".format(command))
        # self.item_id = item_id
        self.command = command
        self.data = data
        self.result = None
        self.processed_by = None

    def __str__(self):
        return "<Job cmd='{}', result='{}'>".format(self.command, self.result)

    @staticmethod
    def from_dict(class_name, j_dict):
        """
        Deserialise a Job from Pyro4
        """
        assert class_name == "job.Job"
        j = Job(j_dict["command"], j_dict["data"])
        # j = Job(j_dict["item_id"], j_dict["data"])
        j.result = j_dict["result"]
        j.processed_by = j_dict["processed_by"]
        return j
