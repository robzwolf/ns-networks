import base64
import os
import socket
import sys
import Pyro4
from Pyro4.util import SerializerBase

from dispatcher_queue import DispatcherQueue
from job import Job

# For "job.Job" we register a deserialisation hook to be able to get these back from Pyro
SerializerBase.register_dict_to_class("job.Job", Job.from_dict)

# For "dispatcher_queue.DispatcherQueue" we register a deserialisation hook to be able to get these back from Pyro
SerializerBase.register_dict_to_class("dispatcher_queue.DispatcherQueue", DispatcherQueue.from_dict)

SERVER_NAME = ""


def handle_upload_init(file_name):
    """
    Handles an upload request with just the file name.
    """
    return {"outcome": "ready to receive"}


def handle_upload_data(file_name, file_contents, high_reliability):
    """
    Handles a full upload request.
    :return:
    """
    # Write the file contents to disk
    with open(file_name + "UPLOADED", "wb") as binary_file:
        binary_file.write(file_contents)

    print("Wrote {} ({:,} bytes) to disk.".format(file_name, len(file_contents)))

    return {"outcome": "success",
            "file_name": file_name,
            "file_size": len(file_contents)}


def handle_list():
    """
    Lists all the files in all directories.
    :return:
    """
    return {"files_list": os.listdir(".")}


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
    :param confirmation:
    :param file_name:
    :return:
    """
    if confirmation:
        os.remove(file_name)
        return {"outcome": "Deleted",
                "file_name": file_name}
    else:
        return {"outcome": "Aborted delete",
                "file_name": file_name}


def process(job):
    # Handle the job appropriately, according to its command
    print("job.command = {}".format(job.command))
    if job.command == "UPLD_INIT":
        job.result = handle_upload_init(job.data["file_name"])
    elif job.command == "UPLD_DATA":
        job.result = handle_upload_data(job.data["file_name"],
                                        base64.b64decode(job.data["file_contents"]["data"]),
                                        job.data["high_reliability"] if "high_reliability" in job.data else False)
    elif job.command == "LIST":
        job.result = handle_list()
    elif job.command == "DWLD":
        job.result = handle_download(job.data["file_name"])
    elif job.command == "DELF_INIT":
        job.result = handle_delete_init(job.data["file_name"])
    elif job.command == "DELF_CONF":
        job.result = handle_delete_full(job.data["file_name"],
                                        job.data["confirm"])

    print("job.result = {}".format(job.result))
    job.processed_by = SERVER_NAME


def main():
    # Handle server name
    global SERVER_NAME
    if len(sys.argv) < 2:
        print("Failed to specify a server name.")
        return
    else:
        SERVER_NAME = sys.argv[1].upper()

    dispatcher = Pyro4.core.Proxy("PYRONAME:distributed_ftp.dispatcher")
    print("This is server '{}'.".format(SERVER_NAME))

    # Register the server with the dispatcher
    dispatcher.register_server(SERVER_NAME)

    # Test hello
    print("hello:", dispatcher.get_hello())

    print("Getting job from dispatcher.")
    while True:
        try:
            # Get this server's queue
            dispatcher_queue = dispatcher.get_server_queue(SERVER_NAME)
            print("dispatcher_queue = {}".format(dispatcher_queue))
            job = dispatcher_queue.get_job()
            process(job)
            print("Putting {} in results queue".format(job))
            dispatcher.put_result(job)
        except ValueError:
            print("No job available yet.")
        else:
            pass


if __name__ == "__main__":
    main()
