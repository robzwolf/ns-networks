# ftp_client.py

import socket
import sys
import argparse

# Constants
DEFAULT_PORT = 1337
HELLO_CHECK = "Successfully connected to server!"

# Global variables
VERBOSE_PRINT = False
PORT = -1


def vprint(contents):
    if VERBOSE_PRINT:
        print(contents)


class FTPClient:

    def __init__(self):
        vprint("FTPClient() constructor called")

    def make_connection(self):

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Connect the socket to the port where the server is listening
        server_address = ("", PORT)
        print("Connecting to {} port {}".format(*sock.getsockname(), PORT))
        sock.connect(server_address)

        try:
            # Send data
            message = b"This is the message. It will be sent back."
            print("Sending {!r}".format(message))
            sock.sendall(message)

            # Look for the response
            amount_received = 0
            amount_expected = len(message)

            while amount_received < amount_expected:
                data = sock.recv(16)
                amount_received += len(data)
                print("Received {!r}".format(data))

        finally:
            print("Closing socket")
            sock.close()


def main():
    # Define arguments
    parser = argparse.ArgumentParser()
    parser.add_argument("-v", "--verbose", help="Enable verbose printing", action="store_true")
    parser.add_argument("-p", "--port", help="Specify a port to connec to", type=int)
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
    client.make_connection()


if __name__ == "__main__":
    main()
