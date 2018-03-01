package xyz.robbie.nsNetworks;

import java.rmi.Remote;
import java.rmi.RemoteException;

public interface FTPServerInterface extends Remote {
    String sayHello() throws RemoteException;
}
