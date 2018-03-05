# ftp_server.py

import socket
import sys
import argparse
import number_converter

# Constants
DEFAULT_PORT = 1337
HELLO_CHECK = b"Successfully connected to server!"
VALID_COMMANDS = ["HELO", "UPLD", "LIST", "DWLD", "DELF", "QUIT"]
SINGLE_OPTION_COMMANDS = ["LIST", "DWLD", "DELF"]
DOUBLE_OPTION_COMMANDS = ["HELO", "UPLD"]
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

    def hello(self, data_1):
        if data_1 != HELLO_CHECK:
            vprint("HELLO_CHECK mismatch. Expected '{}' but received '{}'".format(HELLO_CHECK, data_1))
            return b"MISMATCH"
        else:
            return HELLO_CHECK

    def receive_upload(self, data_1, data_2):
        return bytes("Received {} ({} bytes)".format(data_1, len(data_2)), "utf-8")

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

                command = self.connection.recv(4).decode("utf-8")
                vprint("Received command: {!r}".format(command))
                if command in NO_OPTION_COMMANDS:
                    # self.close_connection()
                    # break
                    if command == "QUIT":
                        print("Client has disconnected.")
                else:

                    data_1 = b""
                    data_2 = b""

                    # Receive DATA_1_LENGTH
                    vprint("Receiving data_1_length...")
                    data_1_length_raw = self.connection.recv(2)
                    vprint("data_1_length_raw = {}".format(data_1_length_raw))
                    data_1_length = number_converter.decode_to_short(data_1_length_raw)
                    vprint("data_1_length = {}".format(data_1_length))

                    # Receive DATA_1
                    vprint("Receiving data_1...")
                    data_1 = self.connection.recv(data_1_length)
                    vprint("data_1 = {}".format(data_1))

                    if command in DOUBLE_OPTION_COMMANDS:
                        # Receive DATA_2_LENGTH
                        vprint("Receiving data_2_length...")
                        data_2_length_raw = self.connection.recv(4)
                        vprint("data_2_length_raw = {}".format(data_2_length_raw))
                        data_2_length = number_converter.decode_to_long(data_2_length_raw)
                        vprint("data_2_length = {}".format(data_2_length))

                        # Receive DATA_2
                        vprint("Receiving data_2...")
                        data_2 = self.connection.recv(data_2_length)
                        vprint("data_2 = {}".format(data_2))

                    response_1 = b""
                    response_2 = b""

                    if command == "HELO":
                        # Handle hello command
                        response_1 = self.hello(data_1)
                        pass
                    elif command == "UPLD":
                        # Handle upload command
                        response_1 = self.receive_upload(data_1, data_2)
                        pass
                    elif command == "LIST":
                        # Handle list command
                        pass
                    elif command == "DWLD":
                        # Handle download command
                        pass
                    elif command == "DELF":
                        # Handle delete file command
                        pass

                    # # Receive the data in small chunks
                    # response_list = []
                    # # response = b""
                    # while True:
                    #     data = self.connection.recv(16)
                    #     vprint("Received {!r}".format(data))
                    #     if data:
                    #         # vprint("Sending data back to the client")
                    #         # self.connection.sendall(data)
                    #         response_list.append(data)
                    #     else:
                    #         vprint("No data from {}".format(client_address))
                    #         break
                    # response = b"".join(response_list)
                    # vprint("Total response: {}".format(response))

                    # Send the data back
                    # self.connection.sendall(response)
                    # break

                    # Send back the response
                    response_message = b""

                    vprint("response_1 = {}".format(response_1))
                    vprint("response_2 = {}".format(response_2))

                    # Prepare response 1
                    vprint("len(response_1) = {}".format(len(response_1)))
                    response_1_length_encoded = number_converter.encode_to_short(len(response_1))
                    response_message += response_1_length_encoded
                    vprint("response_1_length_encoded = {}".format(response_1_length_encoded))
                    response_message += response_1
                    vprint("message = {}".format(response_message))

                    # Prepare response 2
                    vprint("len(response_2) = {}".format(len(response_2)))
                    response_2_length_encoded = number_converter.encode_to_short(len(response_2))
                    response_message += response_2_length_encoded
                    vprint("response_2_length_encoded = {}".format(response_2_length_encoded))
                    response_message += response_2
                    vprint("message = {}".format(response_message))

                    self.connection.sendall(response_message)
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
