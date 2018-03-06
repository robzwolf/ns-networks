# ftp_client.py

import socket
import sys
import argparse

# Constants
DEFAULT_PORT = 1337
HELLO_CHECK = b"Successfully connected to server!"

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

    def make_connection(self):
        """
        Makes a connection to the server by sending a short hello message and checking the response is the same.
        """
        global IS_CONNECTED
        vprint("IS_CONNECTED = {}".format(IS_CONNECTED))

        # Connect the socket to the port where the server is listening
        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server_address = ("", PORT)
        vprint("Connecting to server on port {}".format(PORT))
        self.sock.connect(server_address)

        if not IS_CONNECTED:
            self.send_command(b"HELO")
            print("Made initial connection to server on port " + str(PORT) + "...")
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

    def send_command(self, command):
        """
        Sends a four-character command to the server.
        :param command: The command as a four-byte string, e.g. b"UPLD"
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
            return False
        if type(data) != bytes:
            data = bytes(data, "utf-8")
        data_length = len(data).to_bytes(bytes_length, "big")
        self.sock.sendall(data_length + data)

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
            response_length = int.from_bytes(self.sock.recv(receive_length), "big")
            response = self.sock.recv(response_length)
        else:
            response = self.sock.recv(receive_length)
        return response

    def quit(self):
        print("Quitting...")
        if IS_CONNECTED:
            self.send_command("QUIT")
            self.close_connection()
        sys.exit(0)

    def close_connection(self):
        vprint("Closing socket...")
        self.sock.close()
        global IS_CONNECTED
        IS_CONNECTED = False
        vprint("Connection closed.")

    def menu(self):
        print()
        print("#########################################")
        print("## Status: {}".format("Connected to server " if IS_CONNECTED else "Not connected to server"))
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
        elif command == "DWLD":
            vprint("User wanted DWLD")
        elif command == "DELF":
            vprint("User wanted DELF")
        elif command == "QUIT":
            vprint("User wanted QUIT")
            self.quit()
        else:
            print("Command '{}' not recognised.".format(command))

    def upload_file(self):
        if not IS_CONNECTED:
            print("Error: You are not connected to the server. Use CONN command first.")
        else:
            # Do some upload stuff
            file_name = input("Enter the name of the file to upload: ")
            vprint("User wanted to upload '{}'".format(file_name))
            try:
                with open(file_name, "rb") as binary_file:
                    # Read the whole file at once
                    file_contents = binary_file.read()
                    vprint("Printing file contents... {}".format(file_contents))

                # Upload the command and file name
                vprint("Sending command")
                self.send_command("UPLD")
                vprint("Sending file name")
                self.send_data(file_name, "short")

                # Get the acknowledgement
                vprint("Receiving acknowledgement")
                response = self.receive_data()
                vprint("UPLD mid acknowledgement = {}".format(response))

                # Check server is ready
                if response != b"READY FOR UPLOAD":
                    # Handle the non-ready state appropriately, probably just inform the user and try upload again
                    pass
                else:
                    # Upload the file_contents
                    self.send_data(file_contents, "long")

                    # Get the transfer process results
                    response = self.receive_data().decode("utf-8")

                    if response[:9+len(file_name)] == "Received " + file_name:
                        # Response is basically the results
                        print(response.replace("Received", "Successfully uploaded"))
                    else:
                        # Something went wrong
                        print("Error during upload: {}".format(response))
            except FileNotFoundError as e:
                vprint(e)
                print("Error: File '{}' not found.".format(file_name))


def main():
    # Define arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Enable verbose printing", action="store_true")
    parser.add_argument("-p", "--port", help="Specify a port to connect to", type=int)
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
    client = FTPClient()
    vprint("Made client instance")

    # Start menu
    while True:
        client.menu()


if __name__ == "__main__":
    main()
