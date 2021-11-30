import time
import threading
import math
import os
import struct
import binascii
import socket
import random

thread_status = True


def keep_alive(client_sock, server_addr, interval):
    while True:
        if not thread_status:
            return
        client_sock.sendto(str.encode('4'), server_addr)
        data = client_sock.recv(1500)
        info = str(data.decode())

        if info == '4':
            print("Connection is working")
        else:
            print("connection ended")
            break
        time.sleep(interval)


def start_thread(client_sock, server_addr, interval):
    thread = threading.Thread(target=keep_alive, args=(client_sock, server_addr, interval))
    thread.daemon = True
    thread.start()
    return thread


# here ends tread function
########################################################################################################################

def send_message2(socket, address, msg_type):
    payload = []
    
    if (msg_type == 't'):
        message = str(input('Napiste spravu, ktoru chcete odoslat: '))
    elif (msg_type == 'f'):
        print('Napiste cestu ku suboru: ')
    
    fragment = int(input('Zadajte velkost fragmentu: '))
    while fragment > 1467 or fragment <= 0:
        print("Maximalna velkost fragmentu je 1467 B")
        fragment = int(input("Zvolte si inu velkost fragmentu: "))
    
    if (msg_type == 't'):
        fragments = math.ceil(len(message)/fragment)
        
        while len(message):
            message_fragment = str.encode(message[:fragment], 'utf-8')
            
            message = message[fragment:]
            
        
            

# this function sends message
def send_message(client_socket, server_address, file_text):
    message = 0
    file_name = 0
    message_to_send = 0

    if file_text == "t":
        message = input("Enter the message: ")
    if file_text == "f":
        file_name = input("Input file name: ")
    fragment = int(input("Input fragment size: "))

    while fragment > 1467 or fragment <= 0:
        print("Maximum is 1467 B")
        fragment = int(input("Try to input something different"))

    if file_text == "t":
        number_of_packets = math.ceil(len(message) / fragment)

        print("Number of fragments is:", number_of_packets)

        start_of_communication = ("1" + str(number_of_packets))
        start_of_communication = start_of_communication.encode('utf-8').strip()
        client_socket.sendto(start_of_communication, server_address)

    if file_text == "f":
        size = os.path.getsize(file_name)
        print("File name:", file_name, "Size:", size, "B")
        print("Absolute path:", os.path.abspath(file_name))
        file = open(file_name, "rb")
        file_size = os.path.getsize(file_name)
        number_of_packets = math.ceil(file_size / fragment)

        print("Number of fragments is:", number_of_packets)

        message = file.read()
        start_of_communication = ("2" + str(number_of_packets))
        start_of_communication = start_of_communication.encode('utf-8').strip()
        client_socket.sendto(start_of_communication, server_address)

    packet_number = 0
    number_of_errors = 0

    add_error = input("Do you want errors ? 1 Yes 2 No: ")
    if add_error == "1":
        number_of_errors = int(input("Input maximum number of errors: "))

    while True:
        if len(message) == 0:
            break
        while True:
            if len(message) == 0:
                break

            if file_text == "t":
                message_to_send = message[:fragment]
                message_to_send = str.encode(message_to_send)

            if file_text == "f":
                message_to_send = message[:fragment]

            header = struct.pack("c", str.encode("2")) + struct.pack("HH", len(message_to_send), packet_number)
            crc = binascii.crc_hqx(header + message_to_send, 0)

            if add_error == "1":
                if number_of_errors != 0:
                    if random.random() < 0.5:
                        crc += 1
                        number_of_errors -= 1

            header = struct.pack("c", str.encode("2")) + struct.pack("HHH", len(message_to_send), packet_number, crc)

            client_socket.sendto(header + message_to_send, server_address)

            data, address = client_socket.recvfrom(1500)

            try:
                client_socket.settimeout(10.0)
                data = data.decode()
                if data == "5":
                    packet_number += 1
                    message = message[fragment:]
                else:
                    pass

            except (socket.timeout, socket.gaierror) as e:
                print(e)
                print("Something went wrong")
                return


# this function acts as client
def handle_client(client_socket, server_address):
    global thread_status
    interval = 10
    thread = None

    while True:
        print("0 for exit")
        print("1 for text message")
        print("2 for file message")
        print("3 for keep alive ON")
        print("4 for keep alive OFF")
        print("5 for switching role")
        choice_client = input()

        if choice_client == '0':
            if thread is not None:
                thread_status = False
                thread.join()
            return

        elif choice_client == '1':
            if thread is not None:
                thread_status = False
                thread.join()

            send_message(client_socket, server_address, "t")

        elif choice_client == '2':
            if thread is not None:
                thread_status = False
                thread.join()

            send_message(client_socket, server_address, "f")

        elif choice_client == '3':
            thread_status = True
            thread = start_thread(client_socket, server_address, interval)
            print("Keep alive ON")

        elif choice_client == '4':
            if thread is not None:
                thread_status = False
                thread.join()
                print("Keep alive OFF")

        elif choice_client == '5':
            if thread is not None:
                thread_status = False
                thread.join()
            return
            #switch_users(client_socket, server_address)

        else:
            print("Try to input something different")
            

def client_handshake(client_socket, server_address):
    client_socket.sendto(str.encode("1"), server_address)
    client_socket.settimeout(60)
    data, address = client_socket.recvfrom(1500)
    data = data.decode()
    if data == "1":
        print("Connected to address:", server_address)
        return True
    
    return False
        
# this logs you as client
def login():
    while True:
        address = input("Input IP address of server (localhost): ")
        port = input("Input port: ")
        server_address = (address, int(port))
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            if (client_handshake(client_socket, server_address)):
                handle_client(client_socket, server_address)
        except:
            #print(e)
            print("Connection not working try again")
            continue
            