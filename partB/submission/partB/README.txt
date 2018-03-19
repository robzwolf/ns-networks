# Distributed FTP Client/Server by vzbf32

Ensure Python 3.5 or newer and Pyro4 are installed:
`pip3 install pyro4`

## To run the assignment:
    1) Navigate to the `code/` directory: `cd partB/code/`
    2) Run the name server: `pyro4-ns`
    3) In a separate terminal, run the dispatcher: `python3 dispatcher.py`
    4) In a separate terminal, run the first instance of the server: `python3 server.py mercury`
    5) In a separate terminal, run the second instance of the server: `python3 server.py jupiter`
    6) In a separate terminal, run the third instance of the server: `python3 server.py saturn`
    7) In a separate terminal, run the client: `python3 client.py`
    8) Initially connect to the dispatcher by typing `CONN` in the client and pressing Enter, then follow the menu
       instructions as expected.

## Comments:
    `server.py` takes the server name as its argument, e.g. `python3 server.py mercury` will create a server with the
    name `MERCURY` and create a directory called `SERVER_FILES_MERCURY/` for storing files uploaded to it in.

    `client.py` uploads files stored in the `CLIENT_FILES/` directory.

    To stop any server at any point, use `Ctrl-C` in its terminal.

    The dispatcher has a default timeout of either `4` or `30` seconds (depending on the command being executed), so
    please be patient.

    The dispatcher can handle an arbitrary number of servers, just make sure they have different names.

## Included files:
    partB/
        code/
            CLIENT_FILES/
            client.py
            dispatcher.py
            dispatcher_queue.py
            job.py
            server.py

Some ideas from:
https://github.com/irmen/Pyro4/tree/master/examples/distributed-computing, retrieved 05/03/2018.


NOTE:
Unable to test it works on university machines as I do not have the permissions to install Pyro4.