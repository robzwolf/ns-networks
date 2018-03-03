package xyz.robbie.nsnetworks;

import java.rmi.NotBoundException;
import java.rmi.RemoteException;
import java.rmi.registry.LocateRegistry;
import java.rmi.registry.Registry;
import java.util.Scanner;
import java.io.File;
import java.nio.file.Files;
import java.nio.file.Paths;
import java.nio.file.Path;
import java.io.IOException;

public class FTPClient {
    
    // Constants
    private static final String HOST = "mira1.dur.ac.uk";
    private static final String STUB_NAME = "xyz_robbie_nsnetworks_ftp_server";
    private static final String HELLO_CHECK = "Successfully connected to server!";
    
    // Fields
    private static boolean VERBOSE_PRINT;
    private static int PORT;
    private static FTPServerInterface SERVER_STUB;
    
    
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
    
    private static boolean isConnected() {
        return SERVER_STUB != null;
    }
    
    private static void connectToServer() {
        ePrint("Connecting to server " + HOST + "...");
        try {
            // Get registry
            Registry registry = LocateRegistry.getRegistry(HOST, PORT);
            vPrint("Got registry: " + HOST);

            // Lookup the remote object "server_hello" from registry and create a stub for it
            // FTPServerInterface stub = (FTPServerInterface) registry.lookup(STUB_NAME);
            SERVER_STUB = (FTPServerInterface) registry.lookup(STUB_NAME);
            vPrint("Got stub: " + STUB_NAME);

            // Invoke a remote method
            String response = SERVER_STUB.sayHello();
            vPrint("response: " + response);
            
            if (!response.equals(HELLO_CHECK)) {
                throw new FTPServerClientHelloMismatchException(HELLO_CHECK, response);
            }
            
            vPrint("Currently connected: " + isConnected());

        } catch (RemoteException | NotBoundException e) {
            ePrint("Client exception: " + e);
            e.printStackTrace();
        } catch (FTPServerClientHelloMismatchException e) {
            ePrint("Connection to server failed.");
            vPrint("REASON = " + e);
        }
    }
    
    private static void uploadFile(String localFileName) {
        // Do the file upload
        File toUpload = new File(localFileName);
        vPrint("File '" + localFileName + "' exists() = " + toUpload.exists());
        if (!toUpload.exists()) {
            ePrint("Error: file '" + localFileName + "' not found.");
            return;
        } else {
            try {
                byte[] uploadBytes = Files.readAllBytes(toUpload.toPath());
                for (byte b : uploadBytes) {
                    vPrint(b);
                }
                SERVER_STUB.uploadFile(localFileName, uploadBytes);
            } catch (IOException e) {
                vPrint(e);
                e.printStackTrace();
            }
            
        }
    }
    
    private static void listFiles() {
        // Get list of files from server and list them
    }
    
    private static void downloadFile(String fileName) {
        // Download a file from the server and save it to fileName (locally)
    }
    
    private static void deleteRemoteFile(String fileName) {
        // Delete the remote file fileName
    }
    
    private static void cleanupAndQuit() {
        // Do any necessary clean-ups and then quit the application
        System.exit(0);
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
        
        vPrint("Currently connected: " + isConnected());
        
        
        
        // Do the menu thing
        Scanner scanner = new Scanner(System.in);
        while (true) {
            ePrint("");
            ePrint("## FTP Client Menu ##");
            ePrint("  CONN - connect to server");
            ePrint("  UPLD - upload a file to the server");
            ePrint("  LIST - list the files on the server");
            ePrint("  DWLD - download a file from the server");
            ePrint("  DELF - delete a file from the server");
            ePrint("  QUIT - exit FTP client");
            ePrint("");
            ePrint("Enter a command:");
            String command = scanner.next().toUpperCase();
            ePrint("");
            vPrint("Entered command (in caps) was: " + command);
            
            switch (command) {
                case "CONN": {
                    connectToServer();
                    break;
                }
                case "UPLD": {
                    ePrint("Enter the name of the file to upload:");
                    String fileName = scanner.next();
                    uploadFile(fileName);
                    break;
                }
                case "LIST": {
                    listFiles();
                    break;
                }
                case "DWLD": {
                    downloadFile("");
                    break;
                }
                case "DELF": {
                    deleteRemoteFile("");
                    break;
                }
                case "QUIT": {
                    cleanupAndQuit();
                    break;
                }
                default: {
                    ePrint("\nUnrecognised command: " + command);
                    break;
                }
            }
        }
    }
}
