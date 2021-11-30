import server
import client

client_connect = False
server_connect = False

# Main
while True:
    print("1 for client")
    print("2 for server")
    print("3 to exit")
    choice = input()
    
    if choice == '1':
        client.login()
    elif choice == '2':
        server.server_login()
    elif choice == '3':
        break
    else:
        print("Try to input something different")