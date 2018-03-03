# How to make it all work
1) Store `.java` files in `~/ns-networks-DUR1/src/`
2) SSH into mira1: `ssh vzbf32@mira1.dur.ac.uk`
3) SSH into mira1 from another terminal: `ssh vzbf32@mira1.dur.ac.uk`
4) Navigate to directory: `cd ~/ns-networks-DUR1/src/`
5) Compile Java source files: `javac -d . *.java`
> Let us use the example where the port number is 37002. To use a different port, just use a different number

6) From first terminal, start rmiregistry: `rmiregistry 37002 &`
7) From first terminal, start server: `java example.hello.FTPServer 37002 &`
8) From second terminal, start client: `java example.hello.FTPClient 37002`
