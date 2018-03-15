import os
import socket
import sys
from math import sqrt
import Pyro4
from Pyro4.util import SerializerBase
from work_item import WorkItem

# For 'work_item.WorkItem' we register a deserialisation hook to be able to get these back from Pyro
SerializerBase.register_dict_to_class("work_item.WorkItem", WorkItem.from_dict)

WORKER_NAME = "Worker_{}@{}".format(os.getpid(), socket.gethostname())


## Handlers

def handle_upload_init(file_name):
    """
    Handles an upload request with just the file name.
    """
    return "Ready to receive"


def handle_upload_data(file_name, file_contents, high_reliability):
    """
    Handles a full upload request.
    :return:
    """
    # Write the file contents to disk
    with open(file_name, "wb") as binary_file:
        binary_file.write(file_contents)

    print("Wrote {} ({} bytes) to disk.".format(file_name, len(file_contents)))

    return {"outcome": "Success",
            "file_name": file_name,
            "file_size": len(file_contents)}


def handle_list():
    """
    Lists all the files in all directories.
    :return:
    """
    # TODO: Make this read from all workers
    return {"files_list": os.listdir()}


def handle_download(file_name):
    """
    Handles a download request.
    """
    file_exists = os.path.isfile(file_name)
    if file_exists:
        # Read the file contents and send them
        try:
            with open(file_name, "rb") as binary_file:
                # Read the whole file at once
                file_contents = binary_file.read()
            return file_contents
        except FileNotFoundError as e:
            print("Error: File '{}' not found.".format(file_name))
    else:
        return None


def handle_delete_init(file_name):
    """
    Check if a file exists.
    :param file_name:
    :return:
    """
    return {"file_exists": os.path.isfile(file_name)}


def handle_delete_full(file_name, confirmation):
    """
    Delete a file.
    :param file_name:
    :return:
    """
    # TODO: Make this delete the file from all workers
    if confirmation:
        os.remove(file_name)
        return {"outcome": "Deleted",
                "file_name": file_name}
    else:
        return {"outcome": "Aborted delete",
                "file_name": file_name}




# def factorise(n):
#     """
#     Simple algorithm to find the prime factors of the given number n
#     :param n:
#     :return:
#     """
#
#     def is_prime(n):
#         return not any(x for x in range(2, int(sqrt(n)) + 1) if n % x == 0)
#
#     primes = []
#     candidates = range(2, n + 1)
#     candidate = 2
#     while not primes and candidate in candidates:
#         if n % candidate == 0 and is_prime(candidate):
#             primes = primes + [candidate] + factorise(n // candidate)
#         candidate += 1
#     return primes


## Pyro stuff

def process(item):
    print("Factorising {} --> ".format(item.data))
    sys.stdout.flush()
    # Handle the work item appropriately, according to its command
    if item.command == "UPLD_INIT":
        item.result = handle_upload_init(item.data["file_name"])
    elif item.command == "UPLD_DATA":
        item.result = handle_upload_data(item.data["file_name"],
                                         item.data["file_contents"],
                                         item.data["high_reliability"] if "high_reliability" in item.data else False)
    elif item.command == "LIST":
        item.result = handle_list()
    elif item.command == "DWLD":
        item.result = handle_download(item.data["file_name"])
    elif item.command == "DELF_INIT":
        item.result = handle_delete_init(item.data["file_name"])
    elif item.command == "DELF_CONF":
        item.result = handle_delete_full(item.data["file_name"],
                                         item.data["confirm"])

    print(item.result)
    item.processed_by = WORKER_NAME


def main():
    dispatcher = Pyro4.core.Proxy("PYRONAME:distributed_ftp.dispatcher")
    print("This is worker {}".format(WORKER_NAME))
    print("getting work from dispatcher.")
    while True:
        try:
            item = dispatcher.get_work()
        except ValueError:
            print("No work available yet.")
        else:
            process(item)
            dispatcher.put_result(item)


if __name__ == "__main__":
    main()
