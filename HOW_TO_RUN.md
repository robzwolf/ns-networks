# How to make it all work
1) Store `.java` files in `~/ns-networks-DUR1/src/`
2) SSH into mira1: `ssh vzbf32@mira1.dur.ac.uk`
3) SSH into mira1 from another terminal: `ssh vzbf32@mira1.dur.ac.uk`
4) Compile Java source files: `javac -d . *.java`
5) From first terminal, start rmiregistry: `rmiregistry 1099 &`
6) From first terminal, start server: `java example.hello.FTPServer &`
7) From second terminal, start client: `java example.hello.FTPClient`
