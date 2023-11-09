##############################################################################
# server.py
##############################################################################

import socket
import select
import chatlib

# GLOBALS
users = {}
questions = {}
logged_users = {}

ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"
MAX_MSG_LENGTH = 1024


# HELPER SOCKET METHODS

def build_and_send_message(conn, code, data):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), data (str)
    Returns: Nothing
    """
    print(f'code:{code}, data:{data}')
    full_msg = chatlib.build_message(code, data)
    print("[SERVER] ", full_msg)  # Debug print
    conn.send(full_msg.encode())


# Implement Code
def recv_message_and_parse(conn):
    """
    Recieves a new message from given socket,
    then parses the message using chatlib.
    Paramaters: conn (socket object)
    Returns: cmd (str) and data (str) of the received message.
    If error occured, will return None, None
    """
    full_msg = conn.recv(1024).decode()
    print("[CLIENT] ", full_msg)  # Debug print
    cmd, data = chatlib.parse_message(full_msg)

    print(f'cmd: {cmd}, data: {data} ')
    return cmd, data


# Data Loaders #

def load_questions():
    """
    Loads questions bank from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: questions dictionary
    """
    questions = {
        2313: {"question": "How much is 2+2", "answers": ["3", "4", "2", "1"], "correct": 2},
        4122: {"question": "What is the capital of France?", "answers": ["Lion", "Marseille", "Paris", "Montpellier"],
               "correct": 3}
    }

    return questions


def load_user_database():
    """
    Loads users list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    users = {
        "test": {"password": "test", "score": 0, "questions_asked": []},
        "yossi": {"password": "123", "score": 50, "questions_asked": []},
        "master": {"password": "master", "score": 200, "questions_asked": []}
    }
    return users


# SOCKET CREATOR

def setup_socket():
    """
    Creates new listening socket and returns it
    Recieves: -
    Returns: the socket object
    """
    server_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print("Server is up and running")
    server_socket.bind((SERVER_IP, SERVER_PORT))
    server_socket.listen()

    print("Listening for clients...")

    return server_socket


def send_error(conn, error_msg):
    """
    Send error message with given message
    Receives: socket, message error string from called function
    Returns: None
    """
    conn.send(error_msg.encode())


# ________________MESSAGE HANDLING________________


def handle_getscore_message(conn, username):
    global users


# Implement this in later chapters


def handle_logout_message(conn):
    """
    Closes the given socket (in laster chapters, also remove user from logged_users dictioary)
    Recieves: socket
    Returns: None
    """
    global logged_users

    conn.close()


def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Recieves: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users dictionary from all functions
    global logged_users  # To be used later

    parts = data.split('#')
    print(f'parts: {parts}')
    username = parts[0]
    user = users.get(username)
    if user:
        if user["password"] == parts[1]:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_ok_msg"], '')
            logged_users += users[user]

        else:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], '')

    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], '')

    return


def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Receives: socket, message code and data
    Returns: None
    """
    global logged_users  # To be used later

    if cmd == chatlib.PROTOCOL_CLIENT["login_msg"]:
        print(f'cmd: {cmd}')
        handle_login_message(conn, data)
    elif cmd == chatlib.PROTOCOL_CLIENT["logout_msg"]:
        handle_logout_message(conn)
    elif cmd == chatlib.PROTOCOL_CLIENT["score_msg"]:
        handle_getscore_message(conn, data)
    elif cmd == chatlib.PROTOCOL_CLIENT["highscore_msg"]:
        return
    elif cmd == chatlib.PROTOCOL_CLIENT["logged_in_user"]:
        return
    elif cmd == chatlib.PROTOCOL_CLIENT["question_msg"]:
        return
    elif cmd == chatlib.PROTOCOL_CLIENT["answer_msg"]:
        return
    else:
        conn.send(ERROR_MSG.encode())


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
    # Initializes global users and questions dictionaries using load functions, will be used later
    global users
    global questions

    users = load_user_database()
    questions = load_questions()

    print("Welcome to Trivia Server!")
    server_socket = setup_socket()

    client_sockets = []
    # messages_to_send = []
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
                    cmd, data = recv_message_and_parse(current_socket)
                    handle_client_message(current_socket, cmd, data)


                except Exception as e:
                    print(f'Connection aborted by client: {e}')
                    # client_sockets.remove(current_socket)
                    # current_socket.close()
                    # print_client_sockets(client_sockets)

            # answer_clients(ready_to_write, messages_to_send)


if __name__ == '__main__':
    main()
