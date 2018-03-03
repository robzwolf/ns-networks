package xyz.robbie.nsnetworks;

import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;

public class FTPClient {
    
    static boolean VERBOSE_PRINT;
    static int PORT;
    static FTPServerInterface SERVER_STUB;
    
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
    
    private static void connectToServer() {
        try {
            // Get registry
            Registry registry = LocateRegistry.getRegistry("mira1.dur.ac.uk", PORT);
            vPrint("Got registry mira1");

            // Lookup the remote object "server_hello" from registry and create a stub for it
            FTPServerInterface stub = (FTPServerInterface) registry.lookup("xyz_robbie_nsnetworks_ftp_server");
            SERVER_STUB = stub;
            vPrint("Got stub server_hello");

            // Invoke a remote method
            String response = stub.sayHello();
            vPrint("response: " + response);

        } catch (RemoteException | NotBoundException e) {
            ePrint("Client exception: " + e);
            e.printStackTrace();
        }
    }
    
    public static void main(String[] args) {
        
        System.out.println("Starting FTPClient application...");
        
        // String host = (args.length < 1) ? null : args[0];
        
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

        connectToServer();
    }
}
