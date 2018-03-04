package xyz.robbie.nsnetworks;

import java.rmi.Remote;
import java.rmi.RemoteException;
import java.io.FileNotFoundException;

public interface FTPServerInterface extends Remote {
    String sayHello() throws RemoteException;
    void uploadFile(String fileName, byte[] fileContents) throws RemoteException;
    byte[] downloadFile(String localFileName) throws RemoteException, FileNotFoundException;
}
