# ftp_server.py

import socket
import sys
import argparse
import short_int

# Constants
DEFAULT_PORT = 1337
HELLO_CHECK = b"Successfully connected to server!"
VALID_COMMANDS = ["HELO", "UPLD", "LIST", "DWLD", "DELF", "QUIT"]
SINGLE_OPTION_COMMANDS = ["HELO", "LIST", "DWLD", "DELF"]
DOUBLE_OPTION_COMMANDS = ["UPLD"]
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

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        vprint(self.sock)

        vprint("Made socket")

        self.connection = None
        vprint("Defined self.connection")

    def say_hello(self):
        return HELLO_CHECK

    def start_listening(self):

        # Bind the socket to the port
        server_address = ("", PORT)
        print("Server now listening on {} port {}".format(*self.sock.getsockname(), PORT))
        self.sock.bind(server_address)

        # Listen for incoming connections
        self.sock.listen(1)

        while True:
            # Wait for a connection
            print("Waiting for a connection...")
            self.connection, client_address = self.sock.accept()
            try:
                vprint("Connection from {}".format(client_address))

                # Let's assume the data is in our required format:
                # ################################################
                # COMMAND (4-bytes)                              #
                # optional DATA_1_LENGTH (2 bytes)               #
                # optional DATA_1 (DATA_1_LENGTH bytes)          #
                # optional DATA_2_LENGTH (4 bytes)               #
                # optional DATA_2 (DATA_2_LENGTH bytes)          #
                # ################################################

                command = self.connection.recv(4)
                vprint("Received command: {!r}".format(command))
                if command in NO_OPTION_COMMANDS:
                    self.close_connection()
                    break
                else:
                    # Receive DATA_1_LENGTH
                    data_1_length_raw = self.connection.recv(2)
                    vprint("data_1_length_raw = {}".format(data_1_length_raw))
                    data_1_length = short_int.decode(data_1_length_raw.decode("utf-8"))
                    vprint("data_1_length = {}".format(data_1_length))



                    # Receive the data in small chunks
                    response_list = []
                    # response = b""
                    while True:
                        data = self.connection.recv(16)
                        vprint("Received {!r}".format(data))
                        if data:
                            # vprint("Sending data back to the client")
                            # self.connection.sendall(data)
                            response_list.append(data)
                        else:
                            vprint("No data from {}".format(client_address))
                            break
                    response = b"".join(response_list)
                    vprint("Total response: {}".format(response))

                    # Send the data back
                    self.connection.sendall(response)
                    break
            finally:
                self.close_connection()

    def close_connection(self):
        vprint("Cleaning up connection...")
        # Clean up the connection
        self.connection.close()
        vprint("Closed connection.")


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
    server.start_listening()


if __name__ == "__main__":
    main()
