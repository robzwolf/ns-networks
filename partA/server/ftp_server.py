# ftp_server.py

import socket
import sys
import argparse
import os

# Constants
DEFAULT_PORT = 1337
HELLO_CHECK = b"Successfully connected to server!"
VALID_COMMANDS = ["HELO", "UPLD", "LIST", "DWLD", "DELF", "QUIT"]
SINGLE_OPTION_COMMANDS = ["LIST", "DWLD", "DELF"]
ACKNOWLEDGEMENT_NEEDED_COMMANDS = ["HELO", "UPLD"]
NO_OPTION_COMMANDS = ["QUIT"]

# Global variables
VERBOSE_PRINT = False
PORT = -1


def vprint(contents):
    if VERBOSE_PRINT:
        print(contents)


class FTPServer:

    def __init__(self):
        vprint("FTPServer constructor was called")

        self.sock = None
        self.connection = None
        self.initialise_socket()

    def initialise_socket(self):
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        vprint(self.sock)
        vprint("Made socket")
        vprint("Defined self.connection")

    def listen(self):
        # Bind the socket to the port
        server_address = ("", PORT)
        print("Server now listening on port {}".format(PORT))
        self.sock.bind(server_address)

        # Listen for incoming connections
        self.sock.listen(1)

        # Get connection
        while True:
            print("Waiting for a connection...")
            self.connection, client_address = self.sock.accept()
            vprint("Connection from {}".format(client_address))
            break

        self.listen_for_command()

    def listen_for_command(self):
        # Once we have the connection
        while True:
            print("Waiting for command...")
            # Receive the command
            command = self.receive_command()
            vprint("Received command: {!r}".format(command))
            break

        if command == "HELO":
            self.handle_hello()
        elif command == "UPLD":
            self.handle_upload()
        elif command == "LIST":
            self.handle_list()
        elif command == "DWLD":
            self.handle_download()
        elif command == "DELF":
            pass
        elif command == "QUIT":
            self.handle_quit()

    def close_connection(self):
        vprint("Cleaning up connection...")
        # Clean up the connection
        self.connection.close()
        vprint("Closed connection.")

    def receive_command(self):
        """
        Receives a 4-byte command
        :return: A 4-character string
        """
        command = self.connection.recv(4).decode("utf-8")
        return command

    def send_data(self, data, data_length_size="long"):
        """
        Sends variable-length data to the server.
        :param data: The data to send, as bytes
        :param data_length_size: Either "long" or "short" to specify whether the data length is given as 4 or 2 bytes
        """

        # Send the data length
        self.send_data_number(len(data), data_length_size)

        # Send the data itself
        if type(data) != bytes:
            data = bytes(data, "utf-8")
        self.connection.sendall(data)

    def send_data_number(self, number, data_length_size):
        """
        Sends a number to the client. Encodes it as char bytes.
        :param number: The number to send
        :param byte_length: Either "short" or "long" to specify whether to encode the number as 2 or 4 bytes
        """
        if data_length_size == "short":
            bytes_length = 2
        elif data_length_size == "long":
            bytes_length = 4
        else:
            vprint("Invalid data_length_size parameter: {}".format(data_length_size))
            return False
        encoded_number = number.to_bytes(bytes_length, "big", signed=True)
        self.connection.sendall(encoded_number)

    def receive_data(self, variable_length_response=True, data_length_size="long"):
        """
        Receive data from the server, either of fixed or variable length.
        :param variable_length_response: Whether the response is of variable length or fixed (4 bytes)
        :param data_length_size: Either "long" or "short" to specify whether the data length is given as 4 or 2 bytes
        :return: The response data from the server
        """
        if data_length_size == "long":
            receive_length = 4
        elif data_length_size == "short":
            receive_length = 2
        else:
            vprint("Invalid data_length_size parameter: {}".format(data_length_size))
            return b""
        if variable_length_response:
            response_length = int.from_bytes(self.connection.recv(receive_length), "big", signed=True)
            response = self.connection.recv(response_length)
        else:
            response = self.connection.recv(receive_length)
        return response

    def handle_hello(self):
        """
        Handles the HELO command by sending back the HELLO_CHECK message.
        """
        data = self.receive_data(True)
        if data != HELLO_CHECK:
            vprint("HELLO_CHECK mismatch. Expected '{}' but received '{}'".format(HELLO_CHECK, data))
            self.send_data(b"MISMATCH", "long")
        else:
            vprint("HELLO_CHECK match.")
            self.send_data(HELLO_CHECK, "long")
        print("Connected to client.")
        self.listen_for_command()

    def handle_upload(self):
        """
        Receives an upload request from the client.
        """
        # Receive the file name
        file_name = self.receive_data(data_length_size="short").decode("utf-8")
        vprint("Received file name: {}".format(file_name))

        # Acknowledge that we're ready to receive the file contents
        self.send_data("READY FOR UPLOAD")
        vprint("Acknowledging ready for upload...")

        # Receive the file contents
        file_contents = self.receive_data(data_length_size="long")
        vprint("Received file contents, size {} bytes".format(len(file_contents)))

        # Write the file contents to disk
        with open(file_name, "wb") as binary_file:
            binary_file.write(file_contents)
        results = "Received {} ({} bytes).".format(file_name, len(file_contents))
        print(results)

        # Send back transfer process results
        self.send_data(results)

        self.listen_for_command()

    def handle_download(self):
        """
        Receives a download request from the client.
        """
        # Receive the file name
        file_name = self.receive_data(data_length_size="short").decode("utf-8")
        vprint("Received file name: {}".format(file_name))

        file_exists = os.path.isfile(file_name)
        vprint("{} exists: {}".format(file_name, file_exists))
        if file_exists:
            # Send the file size
            file_size = os.path.getsize(file_name)
            vprint("File size: {}".format(file_size))
            self.send_data_number(file_size, "long")

            # Read the file contents and send them
            try:
                with open(file_name, "rb") as binary_file:
                    # Read the whole file at once
                    file_contents = binary_file.read()
                    vprint("Printing file contents... {}".format(file_contents))

                    # Send the file contents using connection.sendall as we have already sent the data length
                    self.connection.sendall(file_contents)
            except FileNotFoundError as e:
                vprint(e)
                print("Error: File '{}' not found.".format(file_name))

        else:
            # Send a -1
            print("Error: Client requested to download a file that does not exist.")
            self.send_data_number(-1, "long")

        self.listen_for_command()

    def handle_list(self):
        """
        Sends a list of files in the current working directory to the client.
        """
        vprint(os.listdir())

    def handle_quit(self):
        print("Client disconnected.")
        self.close_connection()
        self.initialise_socket()
        self.listen()


def main():
    # Define arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Enable verbose printing", action="store_true")
    parser.add_argument("-p", "--port", help="Specify a port to listen on", type=int)
    args = parser.parse_args()

    # Global inits
    global VERBOSE_PRINT
    global PORT

    print("Starting server...")

    # Handle arguments
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
    server = FTPServer()
    vprint("Made server")
    server.listen()


if __name__ == "__main__":
    main()
