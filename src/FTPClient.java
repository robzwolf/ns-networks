package xyz.robbie.nsNetworks;

// package example.hello;

import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class FTPClient {
    
    public static void main(String[] args) {
        
        System.out.println("Starting FTPClient application...");
        
        // String host = (args.length < 1) ? null : args[0];
        
        int port = (args.length < 1) ? 1099 : Integer.parseInt(args[0]);
        
        // Print out program arguments
        for (int i=0; i<args.length; i++) {
            System.out.println("Arg no. " + i + ": " + args[i]);
        }

        try {
            // Get registry
            Registry registry = LocateRegistry.getRegistry("mira1.dur.ac.uk", port);
            System.out.println("Got registry mira1");

            // Lookup the remote object "server_hello" from registry and create a stub for it
            FTPServerInterface stub = (FTPServerInterface) registry.lookup("server_hello");
            System.out.println("Got stub server_hello");

            // Invoke a remote method
            String response = stub.sayHello();
            System.out.println("response: " + response);

        } catch (RemoteException | NotBoundException e) {
            System.out.println("Client exception: " + e);
            e.printStackTrace();
        }
    }
}
