package xyz.robbie.nsnetworks;

// package example.hello;

import java.rmi.AlreadyBoundException;
import java.rmi.registry.Registry;
import java.rmi.registry.LocateRegistry;
import java.rmi.RemoteException;
import java.rmi.server.UnicastRemoteObject;

public class FTPServer implements FTPServerInterface {
    
    static boolean VERBOSE_PRINT;
    static int PORT;

    public FTPServer() {
        System.out.println("FTPServer() constructor was called");
    }
    
    // Only prints if VERBOSE_PRINT is true
    private static boolean vPrint(Object objToPrint) {
        if (VERBOSE_PRINT) {
            System.out.println(objToPrint);
        }
        return VERBOSE_PRINT;
    }
    
    // Easy print (normal print function wrapper)
    private static void ePrint(Object objToPrint) {
        System.out.println(objToPrint);
    }

    public String sayHello() {
        return "Successfully connected to server!";
    }
    
    public static void main(String[] args) {
        System.out.println("Starting FTPServer application...");
        
        /* Handle arguments
         * Use `-v` to enable verbose print
         * Use `-p <port>` (e.g. `-p 50000`) to specify a port, otherwise
         * default 1099 is used
         */
        if (args.length == 0) {
            VERBOSE_PRINT = false;
            PORT = 1099;
        } else if (args.length == 1) {
            switch (args[0]) {
                case "-p": {
                    ePrint("No port specified.");
                    System.exit(0);
                    break;
                }
                case "-v": {
                    VERBOSE_PRINT = true;
                    ePrint("Verbose print is enabled.");
                    PORT = 1099;
                    ePrint("Using port: 1099 (default)");
                    break;
                }
                default: {
                    ePrint("Invalid argument: " + args[0]);
                    System.exit(0);
                    break;
                }
            }
        } else if (args.length == 2) {
            if (args[0].equals("-p")) {
                PORT = Integer.parseInt(args[1]);
                ePrint("Using port: " + PORT);
            } else {
                ePrint("Invalid argument: "+ args[0]);
                System.exit(0);
            }
        } else if (args.length == 3) {
            if (args[0].equals("-v")) {
                VERBOSE_PRINT = true;
                ePrint("Verbose print is enabled.");
                if (!args[1].equals("-p")) {
                    ePrint("Invalid argument: " + args[1]);
                    System.exit(0);
                } else {
                    PORT = Integer.parseInt(args[2]);
                    ePrint("Using port: " + PORT);
                }
            } else if (args[0].equals("-p")) {
                PORT = Integer.parseInt(args[1]);
                ePrint("Using port: " + PORT);
                if (!args[2].equals("-v")) {
                    ePrint("Invalid argument: " + args[2]);
                    System.exit(0);
                } else {
                    VERBOSE_PRINT = true;
                    ePrint("Verbose print is enabled.");
                }
            } else {
                ePrint("Invalid argument: " + args[0]);
                System.exit(0);
            }
        } else {
            ePrint("Too many arguments.");
            System.exit(0);
        }
        
        // Print out program arguments
        for (int i=0; i<args.length; i++) {
            vPrint("Arg no. " + i + ": " + args[i]);
        }
        
        try {
            // Create server object
            FTPServer server = new FTPServer();
            vPrint("Successfully made new FTPServer");

            // Create remote object stub from server object
            FTPServerInterface stub = (FTPServerInterface) UnicastRemoteObject.exportObject(server, 0);
            vPrint("Created stub");

            // Get registry
            Registry registry = LocateRegistry.getRegistry("mira1.dur.ac.uk", PORT);
            vPrint("Got registry mira1");

            // Bind the remote object's stub in the registry
            registry.bind("xyz_robbie_nsnetworks_ftp_server", server);

            // Write ready message to console
            ePrint("\n#################");
            ePrint("# Server ready! #");
            ePrint("#################\n");
        } catch (RemoteException | AlreadyBoundException e) {
            ePrint("Server remote exception: " + e);
            e.printStackTrace();
        }
    }
}
