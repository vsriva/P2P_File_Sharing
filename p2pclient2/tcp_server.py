import SimpleHTTPServer
import SocketServer
import socket
import sys
from socket import AF_INET, SOCK_DGRAM
from random import randint
import thread

def port_gen():
    return 10000+randint(200, 9999)
    

def get_server(PORT):

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

    httpd = SocketServer.TCPServer(("127.0.0.1", PORT), Handler)

    print "Serving at port", PORT
   
    httpd.serve_forever()


def listen_server(PORT):
    HOST = '127.0.0.1'   # Symbolic name, meaning all available interfaces
    #PORT = 6000 # Arbitrary non-privileged port
     
    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print 'Socket created'
    print PORT 
    #Bind socket to local host and port
    s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        s.bind((HOST, PORT))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
         
    print 'Socket bind complete on:'+HOST+":"+str(PORT)
     
    #Start listening on socket
    s.listen(10)
    print 'Socket now listening'
     
    #now keep talking with the client
    while 1:
        #wait to accept a connection - blocking call
        conn, addr = s.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
        data=conn.recv(1024)
        if data=="Connect":
            a=port_gen()
            conn.sendall(str(a))
            print 'Shifted to ' + addr[0] + ':' + str(a)
            conn.close()
            s.shutdown(1)
            s.close()
            
            print 'Socket closed'
            return a        
             

def start_p2pserver (listenport):
    while (True):
        print "Restarted"
        new_port=listen_server(listenport)
        try:
            thread.start_new_thread(get_server, (new_port, ) )
        except:
            print "Error: unable to start thread"


start_p2pserver(6000)        
    
