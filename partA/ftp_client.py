# ftp_client.py
import fileinput
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


class FTPClient:

    def __init__(self):
        vprint("FTPClient() constructor called")

        # Create a TCP/IP socket
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    def make_connection(self):

        response = self.send_data(HELLO_CHECK)
        if response != HELLO_CHECK:
            vprint("HELLO_CHECK mismatch!")

        # Connect the socket to the port where the server is listening
        # server_address = ("", PORT)
        # print("Connecting to {} port {}".format(*self.sock.getsockname(), PORT))
        # self.sock.connect(server_address)

        # try:
        #     # Send data
        #     message = b"This is the message. It will be sent back."
        #     print("Sending {!r}".format(message))
        #     self.sock.sendall(message)
        #
        #     # Look for the response
        #     amount_received = 0
        #     amount_expected = len(message)
        #
        #     while amount_received < amount_expected:
        #         data = self.sock.recv(16)
        #         amount_received += len(data)
        #         print("Received {!r}".format(data))
        #
        # finally:
        #     self.close_connection()

    def send_data(self, data):
        # Connect the socket to the port where the server is listening
        server_address = ("", PORT)
        print("Connecting to {} port {}".format(*self.sock.getsockname(), PORT))
        self.sock.connect(server_address)

        try:
            # Send data
            message = bytes(data)
            print("Sending:\n{!r}".format(message))
            self.sock.sendall(message)

            response = b""

            # Receive the data in small chunks
            while True:
                vprint("Waiting for response size 16")
                chunk = self.sock.recv(16)
                vprint("Received {!r}".format(chunk))
                response += chunk
                if not chunk:
                    vprint("Response was none")
                    break
                # if len(chunk) < 16:
                #     vprint("That was the final transmission")
                #     break
                #     vprint("Sending data back to the client")
                #     self.sock.sendall(data)
                # else:
                #     vprint("No data from server")
                #     break
            vprint("RESPONSE = {}".format(response))

            # Look for the response
            # amount_received = 0
            # amount_expected = len(message)
            #
            # while amount_received < amount_expected:
            #     data = self.sock.recv(16)
            #     amount_received += len(data)
            #     print("Received {!r}".format(data))

        finally:
            self.close_connection()

        return response

    def close_connection(self):
        vprint("Closing socket...")
        self.sock.close()
        print("Connection closed.")

    def menu(self):
        print()
        print("## FTP Client Menu")
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
        elif command == "LIST":
            vprint("User wanted LIST")
        elif command == "DWLD":
            vprint("User wanted DWLD")
        elif command == "DELF":
            vprint("User wanted DELF")
        elif command == "QUIT":
            vprint("User wanted QUIT")
            self.close_connection()
            return -1


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

    # Start menu
    while True:
        if client.menu() == -1:
            sys.exit(0)


if __name__ == "__main__":
    main()
