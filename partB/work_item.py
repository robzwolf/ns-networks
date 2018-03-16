class WorkItem():
    def __init__(self, command, data=None):
        # print("Created WorkItem, cmd={}".format(command))
        # self.item_id = item_id
        self.command = command
        self.data = data
        self.result = None
        self.processed_by = None

    def __str__(self):
        return "<WorkItem cmd='{}', result='{}'>".format(self.command, self.result)

    @staticmethod
    def from_dict(class_name, wi_dict):
        """
        Deserialise a WorkItem from Pyro4
        :param classname:
        :param wi_dict:
        :return:
        """
        assert class_name == "work_item.WorkItem"
        wi = WorkItem(wi_dict["command"], wi_dict["data"])
        # wi = WorkItem(wi_dict["item_id"], wi_dict["data"])
        wi.result = wi_dict["result"]
        wi.processed_by = wi_dict["processed_by"]
        return wi
