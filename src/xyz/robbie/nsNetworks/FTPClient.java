package xyz.robbie.nsNetworks;

import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class FTPClient {
    public static void main(String[] args) {
        String host = (args.length < 1) ? null : args[0];

        try {
            // Get registry
            Registry registry = LocateRegistry.getRegistry("localhost", 1099);

            // Lookup the remote object "server_hello" from registry and create a stub for it
            FTPServerInterface stub = (FTPServerInterface) registry.lookup("server_hello");

            // Invoke a remote method
            String response = stub.sayHello();
            System.out.println("response: " + response);

        } catch (RemoteException | NotBoundException e) {
            System.out.println("Client exception: " + e);
            e.printStackTrace();
        }
    }
}
