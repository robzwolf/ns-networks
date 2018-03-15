# ftp_client.py

import json
import socket
import sys
import argparse

# Constants
import time

DEFAULT_PORT = 1337
HELLO_CHECK = b"Successfully connected to server!"
SOCKET_BUFFER_SIZE = 1024

# Global variables
VERBOSE_PRINT = False
PORT = -1
IS_CONNECTED = False


def vprint(contents):
    if VERBOSE_PRINT:
        print(contents)


class FTPClient:

    def __init__(self):
        vprint("FTPClient() constructor called")
        self.sock = None

    def send_command(self, command):
        """
        Sends a four-character command to the server.
        :param command: The command as a four-character string, e.g. "UPLD"
        """
        if type(command) != bytes:
            command = bytes(command, "utf-8")
        self.sock.sendall(command)

    def send_data(self, data, data_length_size="long"):
        """
        Sends variable-length data to the server.
        :param data: The data to send, as bytes
        :param data_length_size: Either "long" or "short" to specify whether the data length is given as 4 or 2 bytes
        """
        if data_length_size == "long":
            bytes_length = 4
        elif data_length_size == "short":
            bytes_length = 2
        else:
            vprint("Invalid data_length_size parameter: {}".format(data_length_size))
            return

        # Convert the data to bytes if necessary
        if type(data) != bytes:
            data = bytes(data, "utf-8")

        # Calculate the length of the data to send
        data_length = len(data).to_bytes(bytes_length, "big", signed=True)
        vprint("data_length = {}".format(data_length))

        # Send the data length
        self.sock.sendall(data_length)

        # Send the data
        self.sock.sendall(data)

    def receive_data(self, variable_length_response=True, data_length_size="long", receive_length_specific=None):
        """
        Receive data from the server, either of fixed or variable length.
        :param variable_length_response: Whether the response is of variable length or fixed (4 bytes)
        :param data_length_size: Either "long" or "short" to specify whether the data length is given as 4 or 2 bytes
        :param receive_length_specific: If we already know exactly how much data to receive
        :return: The response data from the server
        """
        if data_length_size == "long":
            receive_length = 4
        elif data_length_size == "short":
            receive_length = 2
        elif data_length_size == "none":
            receive_length = 0
        else:
            vprint("Invalid data_length_size parameter: {}".format(data_length_size))
            return b""
        if variable_length_response:
            # If we already know how many bytes to receive, just use `receive_length_specific` as the response length
            if receive_length != 0:
                response_length = int.from_bytes(self.sock.recv(receive_length), "big", signed=True)
            else:
                response_length = receive_length_specific
            vprint("response_length = {}".format(response_length))

            # Loop through and receive the response in chunks
            amount_received = 0
            response = b""

            vprint("Will read {:,} bytes {:,} times".format(SOCKET_BUFFER_SIZE, response_length // SOCKET_BUFFER_SIZE))
            for i in range(response_length // SOCKET_BUFFER_SIZE):
                data = self.sock.recv(SOCKET_BUFFER_SIZE)
                amount_received += len(data)
                response += data
            vprint("Will now read final {:,} bytes".format(response_length % SOCKET_BUFFER_SIZE))
            data = self.sock.recv(response_length % SOCKET_BUFFER_SIZE)
            amount_received += len(data)
            response += data

            vprint("(response_length = {:,}, amount_received = {:,}, len(response) = {:,})".format(response_length,
                                                                                                   amount_received,
                                                                                                   len(response)))
        else:
            response = self.sock.recv(receive_length)
        return response

    def make_connection(self):
        """
        Makes a connection to the server by sending a short hello message and checking the response is the same.
        """
        global IS_CONNECTED
        vprint("IS_CONNECTED = {}".format(IS_CONNECTED))

        # Connect the socket to the port where the server is listening
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ("localhost", PORT)
        vprint("Connecting to server on port {}".format(PORT))
        self.sock.connect(server_address)

        if not IS_CONNECTED:
            self.send_command(b"HELO")
            vprint("Made initial connection to server on port " + str(PORT) + "...")
            self.send_data(HELLO_CHECK)
            response = self.receive_data(variable_length_response=True)
            if response != HELLO_CHECK:
                vprint("HELLO_CHECK mismatch! Expected '{}' but got '{}'.".format(HELLO_CHECK, response))
            else:
                vprint("HELO matched correctly.")
                print("Successfully connected to server.")
                IS_CONNECTED = True
        else:
            print("Already connected to server.")

    def close_connection(self):
        """
        Closes the connection to the server and cleans up.
        :return:
        """
        vprint("Closing socket...")
        self.sock.close()
        global IS_CONNECTED
        IS_CONNECTED = False
        vprint("Connection closed.")

    def upload_file(self):
        """
        Uploads a file to the server.
        """
        if not IS_CONNECTED:
            print("Error: You are not connected to the server. Use CONN command first.")
            return

        file_name = input("Enter the name of the local file to upload: ")
        vprint("User wanted to upload '{}'".format(file_name))
        try:
            with open(file_name, "rb") as binary_file:
                # Read the whole file at once
                file_contents = binary_file.read()
                vprint("len(file_contents) = {:,}".format(len(file_contents)))

            # Send the command and file name
            vprint("Sending UPLD command")
            self.send_command("UPLD")
            vprint("Sending file name")
            self.send_data(file_name, "short")

            # Get the acknowledgement
            vprint("Receiving acknowledgement")
            response = self.receive_data().decode("utf-8")
            vprint("UPLD mid acknowledgement = {}".format(response))

            # Check server is ready
            if response != "READY FOR UPLOAD":
                # Handle the non-ready state appropriately, just inform the user and tell them to try upload again
                print("Error: Server was not ready for upload. Try again.")
                vprint("Acknowledgement = {}".format(response))
                return
            else:
                # Upload the file_contents
                print("Uploading {}...".format(file_name))
                self.send_data(file_contents, "long")

                # Get the transfer process results
                response = self.receive_data().decode("utf-8")

                if response[:9+len(file_name)] == "Received " + file_name:
                    # Response is effectively the results
                    print(response.replace("Received", "Successfully uploaded"))
                else:
                    # Something went wrong
                    print("Error during upload: {}".format(response))
        except FileNotFoundError as e:
            vprint(e)
            print("Error: File '{}' not found.".format(file_name))

    def download_file(self):
        """
        Downloads a file from the server.
        :return:
        """
        if not IS_CONNECTED:
            print("Error: You are not connected to the server. Use CONN command first.")
            return

        file_name = input("Enter the name of the remote file to download: ")
        vprint("User wanted to download '{}'".format(file_name))

        # Start the timer
        t0 = time.time()

        # Send the command and file name
        vprint("Sending DWLD command")
        self.send_command("DWLD")
        vprint("Sending file name")
        self.send_data(file_name, "short")

        # Getting file status (file size or -1 if remote file does not exist)
        file_size_raw = self.receive_data(variable_length_response=False, data_length_size="long")
        file_size = int.from_bytes(file_size_raw, "big", signed=True)
        vprint("File 'size' of '{}' is: {:,}".format(file_name, file_size))

        if file_size == -1:
            # File does not exist
            print("The file does not exist on server")
            return
        else:
            # File does exist
            file_contents = self.receive_data(variable_length_response=True,
                                              data_length_size="none",
                                              receive_length_specific=file_size)
            vprint("File contents = {}".format(file_contents))

            # Write the results to file
            with open(file_name, "wb") as binary_file:
                binary_file.write(file_contents)

            # Stop the timer
            t1 = time.time()
            time_diff = round(t1 - t0, 3)

            results = "Downloaded {} ({:,} bytes) in {:,} seconds.".format(file_name, len(file_contents), time_diff)
            print(results)

    def list_files(self):
        """
        Retrieves a list of files from the current working directory of the server.
        """
        if not IS_CONNECTED:
            print("Error: You are not connected to the server. Use CONN command first.")
            return

        # Send the command
        self.send_command("LIST")

        # Receive the list of files
        files = json.loads(self.receive_data(data_length_size="long").decode("utf-8"))

        vprint("Received files list: {}".format(files))

        print("\nFiles/folders in directory are:")
        for item in files:
            print(" - {}".format(item))

    def delete_file(self):
        """
        Deletes a file from the server, prompting the user for confirmation.
        """
        if not IS_CONNECTED:
            print("Error: You are not connected to the server. Use CONN command first.")
            return

        file_name = input("Enter the name of the remote file to delete: ")
        vprint("User wanted to delete '{}'".format(file_name))

        # Send the command and file name
        vprint("Sending DELF command")
        self.send_command("DELF")
        vprint("Sending file name")
        self.send_data(file_name, "short")

        file_exists_num = int.from_bytes(self.receive_data(variable_length_response=False, data_length_size="long"),
                                         "big",
                                         signed=True)
        if file_exists_num == 1:
            file_exists = True
        elif file_exists_num == -1:
            print("The file does not exist on the server.")
            return
        else:
            # Abort
            return

        vprint("file_exists = {}".format(file_exists))

        # Ask the user for confirmation
        confirmation = ""
        while confirmation != "Y" and confirmation != "N":
            confirmation = input("Are you sure you want to delete '{}'? [Y/N]: ".format(file_name)).upper()

        vprint("confirmation = {}".format(confirmation))

        # Send the confirmation to the server
        self.send_data(confirmation, "long")

    def quit(self):
        """
        Cleans up and exits the application.
        :return:
        """
        print("Quitting...")
        if IS_CONNECTED:
            self.send_command("QUIT")
            self.close_connection()
        sys.exit(0)

    def menu(self):
        print()
        print("#########################################")
        print("   Status: {}\n".format("Connected to server " if IS_CONNECTED else "Not connected to server"))
        print("## FTP Client Menu ##")
        print("   CONN - connect to server")
        print("   UPLD - upload a file to the server")
        print("   LIST - list the files on the server")
        print("   DWLD - download a file from the server")
        print("   DELF - delete a file from the server")
        print("   QUIT - exit FTP client")
        print()
        command = input("Enter a command: ").upper()
        vprint("cmd was {}".format(command))
        if command == "CONN":
            vprint("User wanted CONN")
            self.make_connection()
        elif command == "UPLD":
            vprint("User wanted UPLD")
            self.upload_file()
        elif command == "LIST":
            vprint("User wanted LIST")
            self.list_files()
        elif command == "DWLD":
            vprint("User wanted DWLD")
            self.download_file()
        elif command == "DELF":
            vprint("User wanted DELF")
            self.delete_file()
        elif command == "QUIT":
            vprint("User wanted QUIT")
            self.quit()
        else:
            print("Command '{}' not recognised.".format(command))


def main():
    # Define command-line arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Enable verbose printing", action="store_true")
    parser.add_argument("-p", "--port", help="Specify a port to connect to", type=int)
    args = parser.parse_args()

    # Global inits
    global VERBOSE_PRINT
    global PORT

    print("Starting server...")

    # Handle command-line arguments
    if args.verbose:
        VERBOSE_PRINT = True
        vprint("Verbose printing is enabled.")
    vprint("Verbose status was {}".format(args.verbose))
    vprint("VERBOSE_PRINT = {}".format(VERBOSE_PRINT))
    if args.port is not None:
        PORT = args.port
        print("Using port:", PORT)
    else:
        PORT = DEFAULT_PORT
        print("Using port: {} (default)".format(PORT))
    vprint("Arg port was {}".format(args.port))

    vprint("main() called")

    # Make server
    client = FTPClient()
    vprint("Made client instance")

    # Start menu
    while True:
        client.menu()


if __name__ == "__main__":
    main()
