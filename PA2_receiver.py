#!/usr/bin/env python3
# Last updated: Oct, 2021

import sys
import time
import socket
import datetime 
from checksum import checksum, checksum_verifier

CONNECTION_TIMEOUT = 60 # timeout when the receiver cannot find the sender within 60 seconds
FIRST_NAME = "FIRSTNAME"
LAST_NAME = "LASTNAME"

def start_receiver(server_ip, server_port, connection_ID, loss_rate=0.0, corrupt_rate=0.0, max_delay=0.0):
    """
     This function runs the receiver, connnect to the server, and receiver file from the sender.
     The function will print the checksum of the received file at the end. 
     The checksum is expected to be the same as the checksum that the sender prints at the end.

     Input: 
        server_ip - IP of the server (String)
        server_port - Port to connect on the server (int)
        connection_ID - your sender and receiver should specify the same connection ID (String)
        loss_rate - the probabilities that a message will be lost (float - default is 0, the value should be between 0 to 1)
        corrupt_rate - the probabilities that a message will be corrupted (float - default is 0, the value should be between 0 to 1)
        max_delay - maximum delay for your packet at the server (int - default is 0, the value should be between 0 to 5)

     Output: 
        checksum_val - the checksum value of the file sent (String that always has 5 digits)
    """

    print("Student name: {} {}".format("Nicholas", "Ankiewicz"))
    print("Start running receiver: {}".format(datetime.datetime.now()))

    checksum_val = "00000"
    def make_ack(ack_num):
        if (ack_num != 0 and ack_num != 1):
            print("Invalid ack_num")
            return None
        ack = "  {}                      ".format(ack_num)
        
        if len(ack) != 25:
            print("Ack lenght error")
            return None
        ack = ack + checksum(ack)
        if len(ack) != 30:
            print("checksum length error")
            return None
        if not checksum_verifier(ack):
            print("Checksum validation incorrect")
            return None
        return ack
    
    def flip_bit(num):
        if num == 0:
            return 1
        return 0
    def connect_gaia(ip, port, id):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        
        if ip == "gaia.cs.umass.edu":
            s.connect(("127.0.0.1", 65500))
            s.sendall(("HELLO R {} {} {} {}".format(loss_rate, corrupt_rate, max_delay, id)).encode())
            while(True):
                recieved_gaia = s.recv(1024)
                recieved_gaia = recieved_gaia.decode()
                if recieved_gaia.count("WAITING") > 0:
                    continue
                else:
                    break
            if recieved_gaia.count("OK") > 0:
                print("{} {}".format(recieved_gaia, datetime.datetime.now()))
                return s
            elif recieved_gaia.count("ERROR") > 0:
                print("Cannot connect to gaia.cs.umass.edu, error message: " + recieved_gaia)
            else:
                print(recieved_gaia)
        else:
            s.bind((ip, int(port)))
            s.listen(5)
            c_sock, c_address = s.accept()
            return c_sock

    cur_seq_num = 0
    file_recieved = ""
    num_recieved = 0
    c_sock = connect_gaia(server_ip, server_port, connection_ID)
    while (True):
        try:
            recieved = c_sock.recv(1024)
            recieved = recieved.decode()
        except:
            break
        if recieved == "":
            break
        recv_seq_num = int(recieved[0])
        data = recieved[4:24]
        num_recieved += 1
        if not checksum_verifier(recieved) or recv_seq_num != cur_seq_num:
            a = make_ack(flip_bit(cur_seq_num))
            try:
                c_sock.sendall(a.encode())
            except:
                break
        else:
            
            if recv_seq_num == cur_seq_num:
                try:
                    c_sock.sendall(make_ack(cur_seq_num).encode())
                except:
                    break
                cur_seq_num = flip_bit(cur_seq_num)
                file_recieved += data

    checksum_val = checksum(file_recieved)
        


    print("Finish running receiver: {}".format(datetime.datetime.now()))

    # PRINT STATISTICS
    # PLEASE DON'T ADD ANY ADDITIONAL PRINT() AFTER THIS LINE
    print("File checksum: {}".format(checksum_val))

    return checksum_val

 
if __name__ == '__main__':
    # CHECK INPUT ARGUMENTS
    if len(sys.argv) != 7:
        print("Expected \"python PA2_receiver.py <server_ip> <server_port> <connection_id> <loss_rate> <corrupt_rate> <max_delay>\"")
        exit()
    server_ip, server_port, connection_ID, loss_rate, corrupt_rate, max_delay = sys.argv[1:]
    # START RECEIVER
    start_receiver(server_ip, int(server_port), connection_ID, loss_rate, corrupt_rate, max_delay)
