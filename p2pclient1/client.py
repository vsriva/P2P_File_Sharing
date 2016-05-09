import socket
import sys
import thread
import os
import random
import httplib
import time
import SimpleHTTPServer
import SocketServer
from random import randint
import filecmp

global temp_data, sequence, estiRTT, devRTT, fragid
mtu = 128
server_host = "127.0.0.1"
server_port = 65000
host = "127.0.0.1"
port = 65000+random.randint(1, 500)
dict_list_files = []
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
temp_data = ""
fragid = ""
sequence = random.randint(1, 100)
estiRTT = 0.1
devRTT = 0



def port_gen():
    return 10000+randint(200, 9999)
    

def get_server(PORT):

    Handler = SimpleHTTPServer.SimpleHTTPRequestHandler

    httpd = SocketServer.TCPServer((host, PORT), Handler)

    print "Serving at port", PORT
   
    httpd.serve_forever()


def listen_server(PORT):
    HOST = '127.0.0.1'   # Symbolic name, meaning all available interfaces
    #PORT = 6000 # Arbitrary non-privileged port
     
    t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print 'Socket created'
    print PORT 
    #Bind socket to local host and port
    t.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
    try:
        t.bind((HOST, PORT))
    except socket.error as msg:
        print 'Bind failed. Error Code : ' + str(msg[0]) + ' Message ' + msg[1]
        sys.exit()
         
    print 'Socket bind complete on:'+HOST+":"+str(PORT)
     
    #Start listening on socket
    t.listen(10)
    print 'Socket now listening'
     
    #now keep talking with the client
    while 1:
        #wait to accept a connection - blocking call
        conn, addr = t.accept()
        print 'Connected with ' + addr[0] + ':' + str(addr[1])
        data=conn.recv(1024)
        if data=="Connect":
            a=port_gen()
            conn.sendall(str(a))
            print 'Shifted to ' + addr[0] + ':' + str(a)
            conn.close()
            t.shutdown(1)
            t.close()
            
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
            

def savetofile(txt,file_name):
    current_path = os.getcwd()
    filename = "TEMP.txt"
    filename = current_path + "/share/" + filename
    f=open(filename,'w')
    f.write(txt)
    f.close
    file_manage(file_name)    

def file_manage(filename):
    if filename in os.listdir("share"):
	status=filecmp.cmp("share/TEMP.txt","share/"+filename)
	if status==True:
	    os.remove("share/TEMP.txt")
	else:
	    os.rename("share/TEMP.txt","share/"+filename.split('.')[0]+"_2.txt")

    else:
        os.rename("share/TEMP.txt","share/"+filename.split('.')[0]+".txt")
	


#ip is string, port is int, filename is string
def getfile(ip,port,filename):
        
    error_flag=0
    httpServ = httplib.HTTPConnection(ip, port)
    httpServ.connect()

    httpServ.request('GET', "/share/"+filename)

    response = httpServ.getresponse()
    if response.status == httplib.OK:
        print "200 OK:Saved to file from HTML request"
        savetofile(response.read(),filename)
	error_flag=200
    elif response.status == httplib.BAD_REQUEST:
        print "400 Error:Request not found"
	error_flag=400
    elif response.status == httplib.NOT_IMPLEMENTED:
        print "500 Error:Request not implemented"
	error_flag=500
    elif response.status == httplib.NOT_FOUND:
        print "404 Error:File not found !!!!"
	error_flag=404
    elif response.status == httplib.HTTP_VERSION_NOT_SUPPORTED:
        print "505 Error:HTTP version not supported !!!!"
	error_flag=505
        
    httpServ.close()
    return error_flag


def main_body(port,file_list): 
    status_codes=[]
    try:
        #create an AF_INET, STREAM socket (TCP)
        t = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    except socket.error, msg:
        print 'Failed to create socket. Error code: ' + str(msg[0]) + ' , Error message : ' + msg[1]
        sys.exit();
     
    print 'Socket Created'
     
    host = '127.0.0.1'
     
    remote_ip = '127.0.0.1'
     
    
         
    print 'Ip address of host:' + host + ' : ' + str(port)
     
    #Connect to remote server
    t.connect((remote_ip , port))
     
    print 'Socket Connected to ' + host
     
    #Send some data to remote server
    message = "Connect"
     
    try :
        #Set the whole string
        t.sendall(message)
    except socket.error:
        #Send failed
        print 'Send failed'
        sys.exit()
        
     
    print 'Message send successfully'
    reply = t.recv(4096)
    print 'Received PORT'
    a=int (reply)
    print a
    t.close()
    print 'Socket closed'
    time.sleep(2)
    print "Sending request"
    for files in file_list:
        status_codes.append(getfile(host,a,files))
    return status_codes

def extract_info_s2p(message):
    status = message.split("\r\n")[0].split(" ")[0]
    pharse = message.split("\r\n")[0].split(" ")[1]
    seq = message.split("\r\n")[1].split(" ")[0]
    ack = message.split("\r\n")[1].split(" ")[2]
    name = message.split("\r\n")[2].split(" ")[0]
    size = message.split("\r\n")[2].split(" ")[1]
    body = message.split("\r\n")[4:len(message.split("\r\n"))]

    return status, pharse, seq, ack, name, size, body


def p2s_query_content(file_name):
    input_file = file_name.split(",")
    name = ""
    for item in input_file:
        name = name + "\r\n" + item
    message = "Q" + " " + host + ":" + str(port) + " " + " " + "\r\n" + str(sequence) +" " + " " + "\r\n" + "file_name" + " " + str(sys.getsizeof(file_name)) + "\r\n" + name

    return message


def p2s_inform_update():
    file_list = ""
    file_path = os.getcwd() + "/share"
    file_name = os.listdir(file_path)
    for name in file_name:
        file_list = file_list + "\r\n" + name
    message = "I" + " " + host + ":" + str(port) + " " + file_path + "\r\n" + str(sequence) +" " + " " + "\r\n" + "file_list" + " " + str(sys.getsizeof(file_list)) + "\r\n" + file_list

    return message


def chunks(l, n):
    return [l[i:i + n] for i in range(0, len(l), n)]

def fragment_send(datagram, ID, address):
    data=[]
    size_data = len(datagram);
    frags = int(size_data / 96)
    left = size_data % 96;
    data_seg = chunks(datagram, 96)
    if size_data > 96:
        for i in range(0, frags):
            strlength = str("128");
            strlength = strlength.zfill(3)
            strID = str(ID);
            strID = strID.zfill(3);
            fragflag = "1"
            offset = 12 * i;
            stroffset = str(offset)
            stroffset = stroffset.zfill(4)
            temp = strlength + strID + fragflag + stroffset + data_seg[i]
            time.sleep(0.001)
            s.sendto(temp, address)
    strlength = str(left)
    strlength = strlength.zfill(3)
    strID = str(ID);
    strID = strID.zfill(3);
    fragflag = "0"
    offset = 12 * frags;
    stroffset = str(offset)
    stroffset = stroffset.zfill(4)
    temp = strlength + strID + fragflag + stroffset + data_seg[-1]
    time.sleep(0.001)
    s.sendto(temp, address)
    
    return data

            
def get_user_input(temp_data, sequence, fragid, estiRTT, devRTT):
    user_input = raw_input("1.Inform&Update 2.Query for Content 3.Exit ")
    if user_input == str(3):
        data = "E" + " " + host + ":" + str(port) + " " + " " + "\r\n" + str(sequence) +" " + " " + "\r\n" + " " + " " + " " + "\r\n" + "\r\n" + " "
        sequence = sequence + sys.getsizeof(data)
        fragment_send(data, sequence, (server_host, server_port))
	sys.exit()
    elif user_input == str(1):
        data = p2s_inform_update()
        fragment_send(data, sequence, (server_host, server_port))
        send_time = time.time()
        while True:
            try:
                data, addr = s.recvfrom(mtu)
                sampleRTT = time.time() - send_time
                estiRTT = 0.875 * estiRTT + 0.125 * sampleRTT
                devRTT = 0.75 * devRTT + 0.25 * sampleRTT
                RTT = estiRTT + devRTT
                temp_data = temp_data + data + "/"
                if data[3:6] not in fragid:
                    fragid = fragid + data[3:6] + "/"
                s.settimeout(RTT)
            except socket.timeout:
                data = temp_data.split("/")
                ids = fragid.split("/")
                temp_data = ""
                fragid = ""
                for ID in ids[0:len(ids)-1]:
                    msg_pkt = []
                    for item in data:
                        if item[3:6] == ID:
                            msg_pkt.append(item)
                    msg = []
                    for item in msg_pkt:
                        index = int(item[7:11])/12
                        msg.insert(index, item[11:])
                    str_msg = ''.join(msg)
                    for item in msg_pkt:
                        if item[6] == str(0):
                            if len(msg_pkt) == int(item[7:11])/12 + 1:
                                extracted_info = extract_info_s2p(str_msg)
                                if int(extracted_info[3]) == sequence:
                                    sequence = sequence + sys.getsizeof(data)
                                    print extracted_info[0], extracted_info[1], extracted_info[4], extracted_info[6]
                                    get_user_input(temp_data, sequence, fragid, estiRTT, devRTT)
                        else:
                            print "No Response! Retransmission the message."
                            data = p2s_inform_update()
                            sequence = sequence + sys.getsizeof(data)
                            fragment_send(data, sequence, (server_host, server_port))
                            send_time = time.time()
    elif user_input == str(2):
        user_input_file_name = raw_input("Enter the file name (multiple names use comma to seperate): ")
        data = p2s_query_content(user_input_file_name)
        fragment_send(data, sequence, (server_host, server_port))
        send_time = time.time()
        while True:
            try:
                data, addr = s.recvfrom(mtu)
                sampleRTT = time.time() - send_time
                estiRTT = 0.875 * estiRTT + 0.125 * sampleRTT
                devRTT = 0.75 * devRTT + 0.25 * sampleRTT
                RTT = estiRTT + 4 * devRTT
                temp_data = temp_data + data + "/"
                if data[3:6] not in fragid:
                    fragid = fragid + data[3:6] + "/"
                s.settimeout(RTT)
            except socket.timeout:
                data = temp_data.split("/")
                ids = fragid.split("/")
                temp_data = ""
                fragid = ""
                for ID in ids[0:len(ids)-1]:
                    msg_pkt = []
                    for item in data:
                        if item[3:6] == ID:
                            msg_pkt.append(item)
                    msg = []
                    for item in msg_pkt:
                        index = int(item[7:11])/12
                        msg.insert(index, item[11:])
                    str_msg = ''.join(msg)
                    for item in msg_pkt:
                        if item[6] == str(0):
                            if len(msg_pkt) == int(item[7:11])/12 + 1:
                                extracted_info = extract_info_s2p(str_msg)
                                if int(extracted_info[3]) == sequence:
                                    sequence = sequence + sys.getsizeof(data)
                                    if extracted_info[0] == "404":
                                        print extracted_info[0], extracted_info[1]
                                        get_user_input(temp_data, sequence, fragid, estiRTT, devRTT)
                                    else:
                                        print extracted_info[4], extracted_info[6]
                                        user_input = raw_input("Do you want to download this file? y/n: ")
                                        if user_input == "n":
                                            get_user_input(temp_data, sequence, fragid, estiRTT, devRTT)
                                        elif user_input == "y":
                                            for item in extracted_info[6]:
                                                info = item.split(":")
                                                code = main_body(int(info[2]), [str(info[0])])
	                                    get_user_input(temp_data, sequence, fragid, estiRTT, devRTT)
                                        else:
                                            print "Oops"
                                            get_user_input(temp_data, sequence, fragid, estiRTT, devRTT)
    else:
        data = str(user_input) + " " + host + ":" + str(port) + " " + " " + "\r\n" + str(sequence) +" " + " " + "\r\n" + " " + " " + " " + "\r\n" + "\r\n" + " "
        fragment_send(data, sequence, (server_host, server_port))
        send_time = time.time()
        while True:
            try:
                data, addr = s.recvfrom(mtu)
                sampleRTT = time.time() - send_time
                estiRTT = 0.875 * estiRTT + 0.125 * sampleRTT
                devRTT = 0.75 * devRTT + 0.25 * sampleRTT
                RTT = estiRTT + devRTT
                temp_data = temp_data + data + "/"
                if data[3:6] not in fragid:
                    fragid = fragid + data[3:6] + "/"
                s.settimeout(RTT)
            except socket.timeout:
                data = temp_data.split("/")
                ids = fragid.split("/")
                temp_data = ""
                fragid = ""
                for ID in ids[0:len(ids)-1]:
                    msg_pkt = []
                    for item in data:
                        if item[3:6] == ID:
                            msg_pkt.append(item)
                    msg = []
                    for item in msg_pkt:
                        index = int(item[7:11])/12
                        msg.insert(index, item[11:])
                    str_msg = ''.join(msg)
                    for item in msg_pkt:
                        if item[6] == str(0):
                            if len(msg_pkt) == int(item[7:11])/12 + 1:
                                extracted_info = extract_info_s2p(str_msg)
                                if int(extracted_info[3]) == sequence:
                                    sequence = sequence + sys.getsizeof(data)
                                    print extracted_info[0], extracted_info[1]
                                    get_user_input(temp_data, sequence, fragid, estiRTT, devRTT)
                        else:
                            print "No Response! Retransmission the message."
                            data = p2s_inform_update()
                            sequence = sequence + sys.getsizeof(data)
                            fragment_send(data, sequence, (server_host, server_port))
                            send_time = time.time()
                            


thread.start_new_thread(start_p2pserver, (port, ) )
time.sleep(2)
get_user_input(temp_data, sequence, fragid, estiRTT, devRTT)
