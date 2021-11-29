import binascii
import math
import os
import socket
import struct
import threading
import time
import random


import server
import client

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


# this logs you as client
def client_login():
    while True:
        try:
            client_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
            address = input("Input IP address of server (localhost): ")
            port = input("Input port: ")
            server_address = (address, int(port))
            client_socket.sendto(str.encode(""), server_address)
            client_socket.settimeout(60)
            data, address = client_socket.recvfrom(1500)
            data = data.decode()
            if data == "1":
                print("Connected to address:", server_address)
                client(client_socket, server_address)
        except (socket.timeout, socket.gaierror) as e:
            print(e)
            print("Connection not working try again")
            continue


# logs you as server
def server_login():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = input("Input port: ")
    server_socket.bind(("", int(port)))
    data, address = server_socket.recvfrom(1500)
    server_socket.sendto(str.encode("1"), address)
    print("Established connection from address:", address)
    server(server_socket, address)


# this functions switches roles
def switch_users(change_socket, address):
    while True:
        print("1 for client")
        print("2 for server")
        print("3 to exit")
        choice_switch = input()
        if choice_switch == '1':
            client(change_socket, address)
        elif choice_switch == '2':
            server(change_socket, address)
        else:
            print("Try to input something different")






# Main
while True:
    print("1 for client")
    print("2 for server")
    print("3 to exit")
    choice = input()
    if choice == '1':
        client_login()
    elif choice == '2':
        server_login()
    elif choice == '3':
        break
    else:
        print("Try to input something different")