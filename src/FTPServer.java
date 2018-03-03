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
        System.out.println("Starting FTPServer application...");
        
        // Print out program arguments
        for (int i=0; i<args.length; i++) {
            System.out.println("Arg no. " + i + ": " + args[i]);
        }
        
        int port = (args.length < 1) ? 1099 : Integer.parseInt(args[0]);
        
        try {
            // Create server object
            FTPServer server = new FTPServer();
            System.out.println("Successfully made new FTPServer");

            // Create remote object stub from server object
            FTPServerInterface stub = (FTPServerInterface) UnicastRemoteObject.exportObject(server, 0);
            System.out.println("Created stub");

            // Get registry
            Registry registry = LocateRegistry.getRegistry("mira1.dur.ac.uk", port);
            System.out.println("Got registry mira1");

            // Bind the remote object's stub in the registry
            registry.bind("server_hello", server);

            // Write ready message to console
            System.out.println("\n#################");
            System.out.println("# Server ready! #");
            System.out.println("#################\n");
        } catch (RemoteException | AlreadyBoundException e) {
            System.out.println("Server remote exception:: " + e);
            e.printStackTrace();
        }
    }
}
