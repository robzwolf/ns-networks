class Job:
    def __init__(self, command, data=None, token=None):
        # print("Created Job, cmd={}".format(command))
        self.command = command
        self.data = data
        self.result = None
        self.processed_by = None
        self.token = token

    def __repr__(self):
        return "<Job cmd='{}', processed_by='{}', result='{}', token='{}',\ndata='''{}'''>".format(self.command,
                                                                                                   self.processed_by,
                                                                                                   self.result,
                                                                                                   self.token,
                                                                                                   self.data)

    @staticmethod
    def from_dict(class_name, j_dict):
        """
        Deserialise a Job from Pyro4
        """
        assert class_name == "job.Job"
        j = Job(j_dict["command"], data=j_dict["data"], token=j_dict["token"])
        j.result = j_dict["result"]
        j.processed_by = j_dict["processed_by"]
        return j
