import copy
import random
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
        self.internal_result_queue = []
        self.USED_RANDOM_NUMS = []
        self.UPLD_TOKEN_DICT = {}

    def gen_unused_random_num(self):
        print("gen_unused_random_num() called")
        num = random.randint(10 ** 20, 10 ** 21)
        while num in self.USED_RANDOM_NUMS:
            num = self.gen_unused_random_num()
        print("Returning {}".format(num))
        return num

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
            # Get number of files from each server and upload to the server with the least files
            list_job = Job("LIST")
            self.put_job_in_all_queues(list_job)
            list_job_results = self.get_internal_results_from_all_servers()
            print("list_job_results = {}".format(list_job_results))

            # Use the server with the fewest files stored on it
            result_to_use = list_job_results[0]
            print("First, using result={}".format(result_to_use))
            for each_result in list_job_results:
                print("In for loop, iter={}".format(each_result))
                # print(len(each_result.result["files_list"]))
                # print(len(result_to_use.result["files_list"]))
                if len(each_result.result["files_list"]) < len(result_to_use.result["files_list"]):
                    result_to_use = each_result
                print("End of this iter")
            print("Using result={}".format(result_to_use))

            # Upload the file to the chosen server
            print("Sending UPLD_INIT job to {}".format(result_to_use.processed_by))
            self.server_queues[result_to_use.processed_by].put_job(job)

            result = self.get_internal_result_from_server(result_to_use.processed_by)
            print("result of upload= {}".format(result))

            # Assign a token to the ongoing upload job so we can associate the client's UPLD_DATA command
            # with the server we should upload to (while still hiding information about the servers from
            # the client)
            token = self.gen_unused_random_num()
            self.UPLD_TOKEN_DICT[token] = result_to_use.processed_by
            result.processed_by = None
            result.token = token
            print("result is now = {}".format(result))

            self.put_external_result(result)

        elif job.command == "UPLD_DATA":

            # Check we recognise the token
            if job.token not in self.UPLD_TOKEN_DICT:
                print("UNRECOGNISED TOKEN: {}".format(job.token))
                return

            # Pass the job onto the server associated with the job token
            server_name = self.UPLD_TOKEN_DICT[job.token]
            print("Putting into server '{}' job={}".format(server_name, job))
            self.put_job_in_specific_server_queue(job, server_name)

            # Get the result from the server and pass it back to the client
            result = self.get_internal_result_from_server(server_name)
            print("Passing back to client result of UPLD_DATA, which was = {}".format(result))
            self.put_external_result(result)

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

    def put_job_in_all_queues(self, job):
        """
        Puts a job in all server queues.
        """
        for sn in self.server_queues.keys():
            self.server_queues[sn].put_job(job)
            print("Put job={} into queue with name '{}'".format(job, sn))

    def put_job_in_specific_server_queue(self, job, server_name):
        self.server_queues[server_name].put_job(job)

    def get_internal_results_from_all_servers(self, timeout=6):
        start_time = time()
        print("Getting internal results from all servers, start_time={:,}...".format(round(start_time, 2)))
        results = []
        while len(results) < len(self.server_queues.keys()) and time() < start_time + timeout:
            print("Begin next loop iteration")
            result = self.get_internal_result()
            if result:
                results.append(result)
            print("Got to end of loop iteration")
        print("Returning results...")
        return results

    def get_internal_result_from_server(self, server_name):
        print("Getting internal result from server '{}'...".format(server_name))
        while True:
            for i in range(len(self.internal_result_queue)):
                if self.internal_result_queue[i].processed_by == server_name:
                    return_result = copy.deepcopy(self.internal_result_queue[i])
                    del self.internal_result_queue[i]
                    return return_result

    def put_external_result(self, job_result):
        print("Server '{}' put result '{}' in results_queue".format(job_result.processed_by, job_result.result))
        self.result_queue.append(job_result)

    def get_external_result(self):
        print("Client requested result")
        while True:
            if len(self.result_queue) > 0:
                result = copy.deepcopy(self.result_queue[0])
                print("Result is '{}'".format(result))
                del self.result_queue[0]
                print("Returning result=\"{}\" to client".format(result))
                return result

    def put_internal_result(self, job_result):
        print("Server '{}' put internal result '{}' in results_queue".format(job_result.processed_by, job_result.result))
        self.internal_result_queue.append(job_result)

    def get_internal_result(self):
        print("Server requested internal result")
        if len(self.internal_result_queue) > 0:
            result = copy.deepcopy(self.internal_result_queue[0])
            print("Result is '{}'".format(result))
            del self.internal_result_queue[0]
            return result


# Main program
Pyro4.Daemon.serveSimple({
    Dispatcher: "distributed_ftp.dispatcher"
})
print("Dispatcher running")
