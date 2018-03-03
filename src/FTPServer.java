package xyz.robbie.nsNetworks;

// package example.hello;

import java.rmi.AlreadyBoundException;
import java.rmi.registry.Registry;
import java.rmi.registry.LocateRegistry;
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;

public class FTPServer implements FTPServerInterface {

    public FTPServer() {
        System.out.println("FTPServer() constructor was called");
    }

    public String sayHello() {
        return "Successful remote invocation!";
    }

    public static void main(String[] args) {
        try {
            // Create server object
            FTPServer server = new FTPServer();
            System.out.println("Successfully made new FTPServer");

            // Create remote object stub from server object
            FTPServerInterface stub = (FTPServerInterface) UnicastRemoteObject.exportObject(server, 0);

            // Get registry
            Registry registry = LocateRegistry.getRegistry("mira1.dur.ac.uk", 1099);

            // Bind the remote object's stub in the registry
            registry.bind("server_hello", server);

            // Write ready message to console
            System.out.println("Server ready");
        } catch (RemoteException | AlreadyBoundException e) {
            System.out.println("Server remote exception:: " + e);
            e.printStackTrace();
        }
    }
}
