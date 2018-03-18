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
SUBDIR = ""


def handle_upload_init(file_name):
    """
    Handles an upload request with just the file name.
    """
    return {"outcome": "ready to receive"}


def handle_upload_data(file_name, file_contents):
    """
    Handles a full upload request.
    :return:
    """
    # Write the file contents to disk
    with open(SUBDIR + file_name, "wb") as binary_file:
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
    return {"files_list": os.listdir(SUBDIR), "outcome": "success"}


def handle_download(file_name):
    """
    Handles a download request.
    """
    file_exists = os.path.isfile(file_name)
    if file_exists:
        # Read the file contents and send them
        try:
            with open(SUBDIR + file_name, "rb") as binary_file:
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
    return {"file_exists": os.path.isfile(SUBDIR + file_name)}


def handle_delete_full(file_name, confirmation):
    """
    Delete a file.
    :param confirmation:
    :param file_name:
    :return:
    """
    if confirmation == "Y":
        try:
            os.remove(SUBDIR + file_name)
            print("Removed '{}' from file system.".format(file_name))
        except FileNotFoundError as e:
            print("File '{}' did not exist for deletion, but it doesn't matter.".format(file_name))
        return {"outcome": "success",
                "file_name": file_name}
    else:
        return {"outcome": "aborted delete due to client cancellation",
                "file_name": file_name}


def process(job):
    # Handle the job appropriately, according to its command
    print("job.command = {}".format(job.command))
    if job.command == "UPLD_INIT":
        job.result = handle_upload_init(job.data["file_name"])
    elif job.command == "UPLD_DATA":
        job.result = handle_upload_data(job.data["file_name"],
                                        base64.b64decode(job.data["file_contents"]["data"]))
    elif job.command == "LIST":
        job.result = handle_list()
    elif job.command == "DWLD":
        job.result = handle_download(job.data["file_name"])
    elif job.command == "DELF_INIT":
        job.result = handle_delete_init(job.data["file_name"])
    elif job.command == "DELF_CONF":
        job.result = handle_delete_full(job.data["file_name"],
                                        job.data["confirmation"])

    print("job.result = {}".format(job.result))
    job.processed_by = SERVER_NAME
    job.data = None
    return job


def main():
    # Handle server name
    global SERVER_NAME
    if len(sys.argv) < 2:
        print("Failed to specify a server name.")
        return
    else:
        SERVER_NAME = sys.argv[1].upper()

    # Make a subdirectory to store this server's files in
    global SUBDIR
    SUBDIR = "./SERVER_FILES_" + SERVER_NAME + "/"
    if not os.path.exists(SUBDIR):
        os.makedirs(SUBDIR)
        print("Made directory {}".format(SUBDIR))

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
            result = process(job)
            print("Putting {} in internal results queue".format(result))
            dispatcher.put_internal_result(result)
        except ValueError:
            print("No job available yet.")
        else:
            pass


if __name__ == "__main__":
    main()
