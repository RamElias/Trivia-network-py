import socket
import time
import select

SERVER_IP = "0.0.0.0"
SERVER_PORT = 5555
MAX_MSG_LENGTH = 1024


def print_client_sockets(client_sockets):
    for c in client_sockets:
        print("\t", c.getpeername())


def answer_clients(ready_to_write, messages_to_send):
    for message in messages_to_send:
        current_socket, data = message
        if current_socket in ready_to_write:
            current_socket.send(data.encode())
            messages_to_send.remove(message)


def main():
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Server is up and running")
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()

    print("Listening for clients...")
    client_sockets = []
    messages_to_send = []

    while True:
        ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, client_sockets, [])
        for current_socket in ready_to_read:
            if current_socket == server_socket:
                (client_socket, client_address) = server_socket.accept()
                print("New client Joined!")
                client_sockets.append(client_socket)
                print_client_sockets(client_sockets)
            else:
                print("New data from client")
                try:
                    data = current_socket.recv(MAX_MSG_LENGTH).decode()
                    if data == '':
                        print("Connection close..")
                        client_sockets.remove(current_socket)
                        print_client_sockets(client_sockets)
                        current_socket.close()
                    else:
                        print(f'client sent {data}')
                        messages_to_send.append((current_socket, data))
                except Exception as e:
                    print(f'Connection aborted by client: {e}')
                    client_sockets.remove(current_socket)
                    current_socket.close()
                    print_client_sockets(client_sockets)

            answer_clients(ready_to_write, messages_to_send)


main()
