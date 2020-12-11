# FTP Client/Server by vzbf32

## Included files:
    partA/
        client/
            ftp_client.py
        server/
            ftp_server.py
        README.txt

## Server
### To run the server
1) `cd partA/server/`
2) `python3 ftp_server.py`

    You can use `-p <port>` to specify a port (e.g. `python3 ftp_server.py -p 40404`), otherwise default `1337` is used.
    You can use `-v` to enable verbose printing (not recommended!).

### To stop the server
Press `Ctrl`-`C`


## Client
### To run the client
1) `cd partA/client/`
2) `python3 ftp_client.py`

    You can use `-p <port>` to specify a port (e.g. `python3 ftp_server.py -p 40404`), otherwise default `1337` is used.
    You can use `-v` to enable verbose printing (not recommended!).

### To use the client
1) Initially connect to the server by typing `CONN` and pressing Enter
2) After successful connection, use any other available command and follow the prompts from the terminal

### To stop the client
Use the QUIT command from the main menu
