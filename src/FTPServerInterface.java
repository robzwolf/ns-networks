package xyz.robbie.nsnetworks;

import java.rmi.Remote;
import java.rmi.RemoteException;

public interface FTPServerInterface extends Remote {
    String sayHello() throws RemoteException;
    void uploadFile(String fileName, byte[] fileContents) throws RemoteException;
}
