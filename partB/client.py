import sys
import Pyro4
from Pyro4.util import SerializerBase
from dispatcher_queue import DispatcherQueue
from job import Job
from time import time

# For "job.Job" we register a deserialisation hook to be able to get these back from Pyro
SerializerBase.register_dict_to_class("job.Job", Job.from_dict)

# For "dispatcher_queue.DispatcherQueue" we register a deserialisation hook to be able to get these back from Pyro
SerializerBase.register_dict_to_class("dispatcher_queue.DispatcherQueue", DispatcherQueue.from_dict)

NUMBER_OF_ITEMS = 40

dispatcher = None


def connect():
    global dispatcher
    dispatcher = Pyro4.core.Proxy("PYRONAME:distributed_ftp.dispatcher")


def upload():
    if dispatcher is None:
        print("Error: You are not connected to the server. Use CONN command first.")
        return

    file_name = input("Enter the name of the local file to upload: ")

    try:
        with open(file_name, "rb") as binary_file:
            # Read the file
            file_contents = binary_file.read()

        t0 = time()

        # Send the command and file name
        dispatcher.put_job(Job("UPLD_INIT", {
                                         "file_name": file_name
                                     }))

        # Check the server is ready to receive
        result = dispatcher.get_result().result
        if result != "Ready to receive":
            print("Error, server not ready to receive: {}".format(result))
            return

        # Send the file contents to the server
        dispatcher.put_job(Job("UPLD_DATA", {
                                         "file_name": file_name,
                                         "file_contents": file_contents
                                     }))

        # Get the response from the upload
        result = dispatcher.get_result().result

        t1 = time()

        if result["outcome"] != "success":
            print("Something went wrong. Response was: {}".format(result))
        else:
            print("Successfully uploaded {} ({:,} bytes) in {:,} seconds.".format(result["file_name"],
                                                                                  result["file_size"],
                                                                                  round(t1 - t0, 4)))

    except FileNotFoundError as e:
        print("Error: File '{}' not found.".format(file_name))


def quit_client():
    print("Quitting client...")
    sys.exit(0)


def menu():
    print()
    print("#########################################")
    print("   Status: {}\n".format("Connected to server" if dispatcher is not None else "Not connected to server"))
    print("## FTP Client Menu ##")
    print("   CONN - connect to server")
    print("   UPLD - upload a file to the server")
    print("   LIST - list the files on the server")
    print("   DWLD - download a file from the server")
    print("   DELF - delete a file from the server")
    print("   QUIT - exit FTP client")
    print()
    command = input("Enter a command: ").upper()

    if command == "CONN":
        connect()
    elif command == "UPLD":
        upload()
    elif command == "QUIT":
        quit_client()
    else:
        print("Command not recognised ({})".format(command))


def main():
    while True:
        menu()


if __name__ == "__main__":
    main()
