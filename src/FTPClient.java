package xyz.robbie.nsNetworks;

// package example.hello;

import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class FTPClient {
    
    public static void main(String[] args) {
        
        System.out.println("Called main method");
        
        String host = (args.length < 1) ? null : args[0];

        try {
            // Get registry
            Registry registry = LocateRegistry.getRegistry("mira1.dur.ac.uk", 1099);
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
