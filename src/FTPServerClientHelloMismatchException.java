package xyz.robbie.nsnetworks;

public class FTPServerClientHelloMismatchException extends Exception {
    private String expected;
    private String actual;
    
    public FTPServerClientHelloMismatchException(String expected, String actual) {
        this.expected = expected;
        this.actual = actual;
    }
    
    public String toString() {
        return "Server/client hello mismatch: expected '" + this.expected + "' but received '" + this.actual + "'";
    }
}
