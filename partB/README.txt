## Distributed FTP Client/Server by vzbf32 ##

Some inspiration from:
https://github.com/irmen/Pyro4/tree/master/examples/distributed-computing, retrieved 15/03/2018

Ensure Pyro4 is installed:
`pip3 install pyro4`

NAME SERVER:
    To run the name server:
    `pyro4-ns`


SERVER:
    To run the server:
    2) `python3 server.py <name>`, e.g. `python3 server.py HERCULES` will start a server with the name `HERCULES`















Included files:
    partA/
        client/
            ftp_client.py
        server/
            ftp_server.py
        README.txt

SERVER
    To run the server:
    1) `cd partA/server/`
    2) `python3 ftp_server.py`

    You can use `-p <port>` to specify a port (e.g. `python3 ftp_server.py -p 40404`), otherwise default 1337 is used
    You can use `-v` to enable verbose printing (not recommended!)

    To stop the server:
       Press Ctrl-C


CLIENT
    To run the client:
    1) `cd partA/client/`
    2) `python3 ftp_client.py`

    You can use `-p <port>` to specify a port (e.g. `python3 ftp_server.py -p 40404`), otherwise default 1337 is used
    You can use `-v` to enable verbose printing (not recommended!)

    To use the client:
    1) Initially connect to the server by typing `CONN` and pressing Enter
    2) After successful connection, use any other available command and follow the prompts from the terminal

    To stop the client:
       Use the QUIT command from the main menu
