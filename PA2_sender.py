#!/usr/bin/env python3
# Last updated: Oct, 2021

import sys
import socket
import datetime
from checksum import checksum, checksum_verifier
import select

CONNECTION_TIMEOUT = 60 # timeout when the sender cannot find the receiver within 60 seconds
FIRST_NAME = "FIRSTNAME"
LAST_NAME = "LASTNAME"

def start_sender(server_ip, server_port, connection_ID, loss_rate=0, corrupt_rate=0, max_delay=0, transmission_timeout=60, filename="declaration.txt"):
    """
     This function runs the sender, connnect to the server, and send a file to the receiver.
     The function will print the checksum, number of packet sent/recv/corrupt recv/timeout at the end. 
     The checksum is expected to be the same as the checksum that the receiver prints at the end.

     Input: 
        server_ip - IP of the server (String)
        server_port - Port to connect on the server (int)
        connection_ID - your sender and receiver should specify the same connection ID (String)
        loss_rate - the probabilities that a message will be lost (float - default is 0, the value should be between 0 to 1)
        corrupt_rate - the probabilities that a message will be corrupted (float - default is 0, the value should be between 0 to 1)
        max_delay - maximum delay for your packet at the server (int - default is 0, the value should be between 0 to 5)
        tranmission_timeout - waiting time until the sender resends the packet again (int - default is 60 seconds and cannot be 0)
        filename - the path + filename to send (String)

     Output: 
        checksum_val - the checksum value of the file sent (String that always has 5 digits)
        total_packet_sent - the total number of packet sent (int)
        total_packet_recv - the total number of packet received, including corrupted (int)
        total_corrupted_pkt_recv - the total number of corrupted packet receieved (int)
        total_timeout - the total number of timeout (int)

    """

    print("Student name: {} {}".format("Nicholas", "Ankiewicz"))
    print("Start running sender: {}".format(datetime.datetime.now()))

    checksum_val = "00000"
    total_packet_sent = 0
    total_packet_recv = 0
    total_corrupted_pkt_recv = 0
    total_timeout =  0
    store = ""
    def make_packet(ack_num, seq_num, data):
        if ack_num != 1 and ack_num != 0:
            print("Ack # is not 1 or 0")
            return None
        if ack_num != 1 and ack_num != 0:
            print("Squence # is not 1 or 0")
            return None
        ack_num = str(ack_num)
        seq_num = str(seq_num)
        pcket = "{} {} {} ".format(seq_num, ack_num, data)
        if len(pcket) != 25:
            print("Error making packet")
            return None
        pcket_checksum = checksum(pcket)
        pcket = pcket + pcket_checksum
        if (not checksum_verifier(pcket)):
            print("Error making checksum")
            return None
        return pcket
    def connect_gaia(ip, port, id):
        s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        s.connect((ip, int(port)))
        if ip == "gaia.cs.umass.edu":
            s.sendall(("HELLO S {} {} {} {}".format(loss_rate, corrupt_rate, max_delay, id)).encode())
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
            return s

    def flip_bit(num):
        if num == 0:
            return 1
        return 0

    print("Connecting to server: {}, {}, {}".format(server_ip, server_port, connection_ID))
    s = connect_gaia(server_ip, server_port, connection_ID)
    file = open(filename, 'r')
    ack_num = 0
    seq_num = 0
    recieved_correct_ack_flag = -1
    while (file.tell() < 200):
        data = file.read(20)
        if data == '':
            break
        while (len(data) < 20):
            data += " "
        store += data
        pcket = make_packet(ack_num, seq_num, data)
        if ack_num == None or seq_num == None:
            break
        s.sendall(pcket.encode())
        total_packet_sent += 1
        recieved_correct_ack_flag = -1
        while(recieved_correct_ack_flag != 1):
            read_sock, _, _ = select.select([s], [], [], transmission_timeout)
            if read_sock:
                for s in read_sock:
                    recieved = s.recv(1024)
                    recieved = recieved.decode()
                    total_packet_recv += 1
                    if (checksum_verifier(recieved)):
                        recieved_ack = recieved.split(" ")
                        recieved_ack = list(filter(None, recieved_ack))
                        if int(recieved_ack[0]) == seq_num:
                            recieved_correct_ack_flag = 1
                            seq_num = flip_bit(seq_num)
                            break
                        else:
                            pass
                    else:
                        total_corrupted_pkt_recv += 1
            else:
                total_packet_sent += 1
                total_timeout += 1
                s.sendall(pcket.encode())
    file.close()
    checksum_val = checksum(store)
    ##### END YOUR IMPLEMENTATION HERE #####

    print("Finish running sender: {}".format(datetime.datetime.now()))

    # PRINT STATISTICS
    # PLEASE DON'T ADD ANY ADDITIONAL PRINT() AFTER THIS LINE
    print("File checksum: {}".format(checksum_val))
    print("Total packet sent: {}".format(total_packet_sent))
    print("Total packet recv: {}".format(total_packet_recv))
    print("Total corrupted packet recv: {}".format(total_corrupted_pkt_recv))
    print("Total timeout: {}".format(total_timeout))

    return (checksum_val, total_packet_sent, total_packet_recv, total_corrupted_pkt_recv, total_timeout)
 
if __name__ == '__main__':
    # CHECK INPUT ARGUMENTS
    if len(sys.argv) != 9:
        print("Expected \"python3 PA2_sender.py <server_ip> <server_port> <connection_id> <loss_rate> <corrupt_rate> <max_delay> <transmission_timeout> <filename>\"")
        exit()

    # ASSIGN ARGUMENTS TO VARIABLES
    server_ip, server_port, connection_ID, loss_rate, corrupt_rate, max_delay, transmission_timeout, filename = sys.argv[1:]
    
    # RUN SENDER
    start_sender(server_ip, int(server_port), connection_ID, loss_rate, corrupt_rate, max_delay, float(transmission_timeout), filename)
