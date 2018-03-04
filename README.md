# Networks and Systems Assignment
COMP2211 Networks and Systems – Networks and Distributed Systems assignment.

## Command Line Options
### Verbose Printing `-v` / `--verbose`
Print lots of extra debugging information.

### Specify Port `-p <port>` / `--port <port>`
Run the server/client on the the specified port, e.g. `-p 37001` will run on port `37001`.

## Part A
### How to Run Python Files
1) Navigate to `ns-networks-fresh/partA/`
2) Run the server: `python3 ftp_server.py -p 40404`
3) Run the client: `python3 ftp_client.py -p 40404`

## Part B

### Package
All Java files are in the `xyz.robbie.nsnetworks` package.

### How to Run Java Files
1) Store `.java` files in `~/ns-networks-DUR1/src/`
2) SSH into mira1: `ssh vzbf32@mira1.dur.ac.uk`
3) SSH into mira1 from another terminal: `ssh vzbf32@mira1.dur.ac.uk`
4) Navigate to directory: `cd ~/ns-networks-DUR1/src/`
5) Compile Java source files: `javac -d . *.java`
> Let us use the example where the port number is 37002. To use a different port, just use a different number.

6) From first terminal, start RMI registry: `rmiregistry 37002 &`
7) From first terminal, start server: `java xyz.robbie.nsnetworks.FTPServer -p 37002 &`
8) From second terminal, start client: `java xyz.robbie.nsnetworks.FTPClient -p 37002`


