	
import socket   #for sockets
import sys  #for exit
import httplib
import time

def savetofile(txt,filename):
    f=open(filename,'w')
    f.write(txt)
    f.close



#ip is string, port is int, filename is string
def getfile(ip,port,filename):
    
    httpServ = httplib.HTTPConnection(ip, port)
    httpServ.connect()

    httpServ.request('GET', "/share/"+filename)

    response = httpServ.getresponse()
    if response.status == httplib.OK:
        print "OK:Saved to file from HTML request"
        savetofile(response.read(),filename)
    elif response.status == httplib.BAD_REQUEST:
        print "Error:Request not found"
    elif response.status == httplib.NOT_IMPLEMENTED:
        print "Error:Request not implemented"
    elif response.status == httplib.NOT_FOUND:
        print "Error:File not found !!!!"
    elif response.status == httplib.HTTP_VERSION_NOT_SUPPORTED:
        print "Error:HTTP version not supported !!!!"
        
    httpServ.close()



def main_body(port,file_list): 
    try:
        #create an AF_INET, STREAM socket (TCP)
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
        sys.exit();
     
    print 'Socket Created'
     
    host = '127.0.0.1'
     
    remote_ip = '127.0.0.1'
     
    
         
    print 'Ip address of host:' + host + ' : ' + str(port)
     
    #Connect to remote server
    s.connect((remote_ip , port))
     
    print 'Socket Connected to ' + host
     
    #Send some data to remote server
    message = "Connect"
     
    try :
        #Set the whole string
        s.sendall(message)
    except socket.error:
        #Send failed
        print 'Send failed'
        sys.exit()
        
     
    print 'Message send successfully'
    reply = s.recv(4096)
    print 'Received PORT'
    a=int (reply)
    print a
    s.close()
    print 'Socket closed'
    time.sleep(2)
    print "Sending request"
    for files in file_list:
        getfile("127.0.0.1",a,files)##You can use this for multiple file transfers too


main_body(6000,["frag.py"])
