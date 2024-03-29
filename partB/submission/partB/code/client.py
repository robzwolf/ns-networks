import base64
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
SUBDIR = "./CLIENT_FILES/"
dispatcher = None


def connect():
    """
    Connects to the dispatcher.
    """
    print("Connecting...")
    global dispatcher
    try:
        dispatcher = Pyro4.core.Proxy("PYRONAME:distributed_ftp.dispatcher")
        if dispatcher.get_hello() != "Hello":
            dispatcher = None
            print("Error connecting to server.")
        else:
            print("Connection to server successful.")
    except Exception as e:
        print("Error connecting to server: {}".format(e))


def upload():
    """
    Handles a file upload.
    """
    if dispatcher is None:
        print("Error: You are not connected to the server. Use CONN command first.")
        return

    file_name = input("Enter the name of the local file to upload: ")

    if file_name == "":
        return

    try:
        with open(SUBDIR + file_name, "rb") as binary_file:
            # Read the file
            file_contents = binary_file.read()

        # Ask about high reliability
        hr = ""
        while hr != "Y" and hr != "N":
            hr = input("Use high reliability? [Y/N]: ").upper()

        high_reliability = True if hr == "Y" else False
        print("Using high reliability: {}".format(high_reliability))

        if len(file_contents) > 2 * 2**20:
            print("Warning: This file is large (> 2 MB) and may take a while to upload!")

        print("Uploading...")

        t0 = time()

        # Send the command and file name
        dispatcher.put_job(Job("UPLD_INIT", data={
            "file_name": file_name,
            "high_reliability": high_reliability,
            "file_size": len(file_contents)
        }))

        # Check the server is ready to receive
        result = dispatcher.get_external_result()
        if result.result["outcome"] != "ready to receive":
            print("Error, server not ready to receive: {}".format(result.result["outcome"]))
            return

        # Send the file contents to the server
        upld_data_job = Job("UPLD_DATA",
                            token=result.token,
                            data={"file_name": file_name,
                                  "file_contents": file_contents,
                                  "high_reliability": high_reliability,
                                  "file_size": len(file_contents)})
        dispatcher.put_job(upld_data_job)

        # Get the response from the upload
        result = dispatcher.get_external_result().result

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
    """
    Quits the client.
    :return:
    """
    print("Quitting client...")
    try:
        sys.exit(0)
    except:
        sys.exit(0)


def list_files():
    """
    Gets a list of available files for download from the dispatcher.
    """
    if dispatcher is None:
        print("Error: You are not connected to the server. Use CONN command first.")
        return

    print("Getting list of files...")
    dispatcher.put_job(Job("LIST"))
    result = dispatcher.get_external_result()

    if result.result["outcome"] != "success":
        print("An error occurred retrieving the files list: {}".format(result.result["outcome"]))
        return

    print("\nFiles list is:")
    for file_name in result.result["files_list"]:
        print("  - {}".format(file_name))


def delete_file():
    """
    Deletes a remote file from all servers.
    """
    if dispatcher is None:
        print("Error: You are not connected to the server. Use CONN command first.")
        return

    file_name = input("Enter the name of the remote file to delete: ")

    if file_name == "":
        return

    dispatcher.put_job(Job("DELF_INIT", data={"file_name": file_name}))

    result = dispatcher.get_external_result()

    if result.result["outcome"] != "success":
        print("Something went wrong. Response was: {}".format(result.result["outcome"]))
        return

    if not result.result["file_exists"]:
        print("The file '{}' does not exist on any remote server.".format(file_name))
        return

    confirmation = ""
    while confirmation != "Y" and confirmation != "N":
        confirmation = input("Are you sure you want to delete '{}'? [Y/N]: ".format(file_name)).upper()

    if confirmation == "N":
        return

    dispatcher.put_job(Job("DELF_CONF", data={"file_name": file_name, "confirmation": confirmation}))

    result = dispatcher.get_external_result()

    if result.result["outcome"] != "success":
        print("\nSomething went wrong. Response was: {}".format(result.result["outcome"]))
    else:
        print("\nSuccessfully deleted '{}' from all servers.".format(file_name))


def download_file():
    """
    Downloads a remote file from the dispatcher.
    """
    if dispatcher is None:
        print("Error: You are not connected to the server. Use CONN command first.")
        return

    print()

    file_name = input("Enter the name of the remote file to download: ")

    if file_name == "":
        return

    print("Requesting '{}', please wait...".format(file_name))

    t0 = time()

    dispatcher.put_job(Job("DWLD", data={"file_name": file_name}))

    result = dispatcher.get_external_result()

    if result.result["outcome"] != "success":
        print("Something went wrong. Response was: {}".format(result.result["outcome"]))
        return

    if not result.result["file_exists"]:
        print("The file '{}' does not exist on any remote server.".format(file_name))
    else:
        # Write the file contents to disk
        file_contents = base64.b64decode(result.result["file_contents"]["data"])
        with open(SUBDIR + file_name, "wb") as binary_file:
            binary_file.write(file_contents)
        t1 = time()
        print("Downloaded {} ({:,} bytes) in {:,} seconds.".format(file_name, len(file_contents), round(t1 - t0, 2)))


def menu():
    """
    The client-facing command-line menu.
    """
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
    elif command == "LIST":
        list_files()
    elif command == "DWLD":
        download_file()
    elif command == "DELF":
        delete_file()
    elif command == "QUIT":
        quit_client()
    else:
        print("Command not recognised ({})".format(command))


def main():
    """
    The main function.
    """
    while True:
        menu()


if __name__ == "__main__":
    main()
