import os
import struct
import binascii
import socket

# this function receives message
def receive_message(number_of_all_packets, server_socket, file_message):
    number_of_all_received_packets = 0
    number_of_packets = 0
    full_message = []

    while True:
        if number_of_packets == int(number_of_all_packets):
            break

        while True:
            if number_of_packets == int(number_of_all_packets):
                break

            data, address = server_socket.recvfrom(64965)
            message = data[7:]
            length, packet_number, crc_received = struct.unpack("HHH", data[1:7])
            header = struct.pack("c", str.encode("2")) + struct.pack("HH", len(message), packet_number)
            crc = binascii.crc_hqx(header + message, 0)

            if crc == crc_received:
                print(f"Packet number {number_of_packets} was accepted")
                number_of_packets += 1
                number_of_all_received_packets += 1

                if file_message == "t":
                    full_message.append(message.decode())

                if file_message == "f":
                    full_message.append(message)

                server_socket.sendto(str.encode("5"), address)

            else:
                print(f"Packet number {number_of_packets} was rejected")
                server_socket.sendto(str.encode("3"), address)
                number_of_all_received_packets += 1

    print("number of damaged packets:", number_of_all_received_packets - number_of_packets)
    print("number of all received packets", number_of_all_received_packets)
    print("Number of accepted packets: " + str(number_of_packets))

    if file_message == "t":
        print("Message:", ''.join(full_message))

    if file_message == "f":
        file_name = "photo_receive.jpg"
        file = open(file_name, "wb")

        for frag in full_message:
            file.write(frag)
        file.close()
        size = os.path.getsize(file_name)
        print("Name:", file_name, "Size:", size, "B")
        print("Absolute path:", os.path.abspath(file_name))


# this functions acts like server
def handle_server(server_socket, address):
    while True:
        print("1 - for exit")
        print("2 - for receiving message/file")
        
        choice = input()

        if choice == '1':
            return

        elif choice == "2":
            print('Cakam na subor alebo spravu...')

        try:
            server_socket.settimeout(60)

            
            data = server_socket.recv(1500)
            info = str(data.decode())

            if info == '4':
                print("Keep alive received, Connection is on")
                server_socket.sendto(str.encode("4"), address)
                info = ''

            typ = info[:1]
            if typ == '1':  # text message
                number_of_packets = info[1:]
                print("Incoming message will consist of " + number_of_packets + " packets")
                receive_message(number_of_packets, server_socket, "t")
                break

            if typ == '2':  # file message
                number_of_packets = info[1:]
                print("Incoming file will consist of " + number_of_packets + " packets\n")
                receive_message(number_of_packets, server_socket, "f")
                break

        except socket.timeout:
            print("Client is inactive shutting down")
            server_socket.close()
            return
        
def server_handshake(socket):
    data, address = socket.recvfrom(1500)
    data = data.decode()
    
    if (data == '1'):
        print("Established connection from address:", address)
        socket.sendto(str.encode("1"), address)
        return address, True
    

# logs you as server
def server_login():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    port = input("Input port: ")
    server_socket.bind(("", int(port)))
    
    address, handshake_success = server_handshake(server_socket)
    
    if (handshake_success):
        handle_server(server_socket, address)
    else:
        print('S klientom sa nepodarilo nadviazat spojenie.')
        return