# ftp_server.py

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

class FTPServer:

    def FTPServer():
        vprint("FTPServer constructor was called")

    def say_hello():
        return HELLO_CHECK

    def start_listening():

        # Create a TCP/IP socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

        # Bind the socket to the port
        server_address = ("localhost", 10000)
        print("Starting on {} port {}".format(*server_address))
        sock.bind(server_address)

        # Listen for incoming connections
        sock.listen(1)

        while True:
            # Wait for a connection
            print("Waiting for a connection")
            connection, client_address = sock.accept()
            try:
                print("Connection from", client_address)

                # Receive the data in small chunks and retransmit it
                while True:
                    data = connection.recv(16)
                    print("Received {!r}".format(data))
                    if data:
                        print("Sending data back to the client")
                        connection.sendall(data)
                    else:
                        print("No data from", client_address)
                        break

            finally:
                print("Cleaning up connection")
                # Clean up the connection
                connection.close()
                # sys.exit(0)


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

if __name__ == "__main__":
    main()
