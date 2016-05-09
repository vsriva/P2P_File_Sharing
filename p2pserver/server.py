import socket
import sys
import platform
import thread
import time




global peer_list, file_list, full_list, temp_data, acknowledge
mtu = 128
s = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
host = "127.0.0.1"
port = 65000
s.bind((host, port))
peer_list = []
file_list = []
full_list = []
temp_data = ""
fragid = ""
acknowledge = 0


def create_peer_list(dict_list, host, port):
    dict_list[:] = [d for d in dict_list if d.get("Host") != host or d.get("Port") != port]
    keys = ["Host", "Port"]
    entry = [host, port]
    dict_list.insert(0, dict(zip(keys, entry)))

    return dict_list, keys



def create_full_list(dict_list, dict_list_files, host, port):
    dict_list[:] = [d for d in dict_list if d.get("Host") != host or d.get("Port") != port]
    keys = ["File", "Host", "Port"]
    for file in dict_list_files:
        file_name = file
        entry = [str(file_name), host, port]
        dict_list.insert(0, dict(zip(keys, entry)))

    return dict_list, keys



def search_full_list(file):
    temp_addr = ""
    for item in file:
        for d in full_list:
            if d['File'] == item:
                temp_addr = temp_addr + item + ":" + str(d["Host"]) + ":" + str(d["Port"]) + "\r\n"

    return temp_addr


def s2p_response(seq, name, data):
    temp = str(data).split("\r\n")
    ack = seq
    body = ""
    if len(data) == 0:
        status = "404"
        phrase = "NotFound"
    else:
        status = "200"
        phrase = "OK"
    for item in temp:
        if item != "":
            body = body + "\r\n" + item 
    message = status + " " + phrase + "\r\n" + " " + " " + str(ack) + "\r\n" + name + " " + str(sys.getsizeof(body)) + "\r\n" + body

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

    
def extract_info_p2s(message):
    method = message.split("\r\n")[0].split(" ")[0]
    ip = message.split("\r\n")[0].split(" ")[1].split(":")[0]
    port = message.split("\r\n")[0].split(" ")[1].split(":")[1]
    folder = message.split("\r\n")[0].split(" ")[2]
    seq = message.split("\r\n")[1].split(" ")[0]
    ack = message.split("\r\n")[1].split(" ")[1]
    name = message.split("\r\n")[2].split(" ")[0]
    size = message.split("\r\n")[2].split(" ")[1]
    body = message.split("\r\n")[4:len(message.split("\r\n"))]

    return method, ip, port, folder, seq, ack, name, size, body


def return_file_list(dict_list):
    file_list = []
    for d in dict_list:
        file_list.append(d["File"])
    file_list1 = list(set(file_list))
    
    return file_list1


def handle_msg(message, address, peer_list, full_list, acknowledge, n):
    print n
    extracted_info = extract_info_p2s(message)
    if extracted_info[0] == "E":
        peer_list[:] = [d for d in peer_list if d.get("Host") != extracted_info[1] and d.get("Port") != extracted_info[2]]
        full_list[:] = [d for d in full_list if d.get("Host") != extracted_info[1] and d.get("Port") != extracted_info[2]]
    else:
        print "Got message from: ", addr
        if extracted_info[0] == "I":
            print "Update files from: ", addr
            peer_list, peer_keys = create_peer_list(peer_list, extracted_info[1], extracted_info[2])
            full_list, combined_keys = create_full_list(full_list, extracted_info[8], extracted_info[1], extracted_info[2])
            fragment_send(s2p_response(acknowledge, "file_list", return_file_list(full_list)), acknowledge, address)
        elif extracted_info[0] == "Q":
            print "Query and download request from: ", addr
            fragment_send(s2p_response(acknowledge, "search_result", search_full_list(extracted_info[8])), acknowledge, address)
        else:
            message = "400" + " " + "BadRequest" + "\r\n" + " " + " " + str(acknowledge) + "\r\n" + " " + " " + " " + "\r\n" + "\r\n" + " "
            fragment_send(message, acknowledge, address)


while True:
    try:
        data, addr = s.recvfrom(mtu)
        temp_data = temp_data + data + ","
        if data[3:6] not in fragid:
            fragid = fragid + data[3:6] + ","
        s.settimeout(0.5)
    except socket.timeout:
        data = temp_data.split(",")
        ids = fragid.split(",")
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
                        thread.start_new_thread(handle_msg, (str_msg, addr, peer_list, full_list, ID, ID))
                else:
                    print "Packet loss! Won't send respoonse message."
