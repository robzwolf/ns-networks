# ftp_server.py

import socket
import sys
import argparse

# Constants
DEFAULT_PORT = 1337
HELLO_CHECK = b"Successfully connected to server!"

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

                # Receive the data in small chunks and retransmit it
                while True:
                    data = self.connection.recv(16)
                    vprint("Received {!r}".format(data))
                    if data:
                        vprint("Sending data back to the client")
                        self.connection.sendall(data)
                    else:
                        vprint("No data from {}".format(client_address))
                        break

            finally:
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
