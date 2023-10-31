import socket
import time
server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

server_socket.bind(("0.0.0.0", 8820))
server_socket.listen()
print("Server is up and running")

(client_socket, client_address) = server_socket.accept()
print("client connected")

server_name = "Super server"
data = ""
while True:
    data = client_socket.recv(1024).decode()
    print(f'client send {data}')
    if data.lower() == 'bye':
        data = ' '
    elif data.lower() == 'quit':
        print('closing socket...')
        client_socket.send('Bye'.encode())
        break
    data += f'\nName:{server_name}\nTime:{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}\n'
    client_socket.send(data.encode())

client_socket.close()
server_socket.close()
