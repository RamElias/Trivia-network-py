##############################################################################
# server.py
##############################################################################
import json
import socket
import select
import chatlib
import random

# GLOBALS
users = {}
questions = {}
logged_users = {}
messages_to_send = []

ERROR_MSG = "Error! "
SERVER_PORT = 5678
SERVER_IP = "127.0.0.1"
MAX_MSG_LENGTH = 1024


# HELPER SOCKET METHODS
def answer_clients(ready_to_write):
    global messages_to_send

    for message in messages_to_send:
        current_socket, data = message
        if current_socket in ready_to_write:
            current_socket.send(data.encode())
            messages_to_send.remove(message)


def build_and_send_message(conn, code, data):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), data (str)
    Returns: Nothing
    """
    full_msg = chatlib.build_message(code, data)
    print("[SERVER] ", full_msg)  # Debug print
    messages_to_send.append((conn.getpeername(), full_msg))
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

    return cmd, data


# Data Loaders #

def load_questions(filename="DB/questions.json"):
    """
    Loads questions.json bank from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: questions.json dictionary
    """
    global questions

    try:
        with open(filename, 'r') as file:
            questions = json.load(file)
    except FileNotFoundError:
        questions = {}

    return questions


def load_user_database(filename="DB/users.json"):
    """
    Loads users.json list from file	## FILE SUPPORT TO BE ADDED LATER
    Recieves: -
    Returns: user dictionary
    """
    global users

    try:
        with open(filename, 'r') as file:
            users = json.load(file)
    except FileNotFoundError:
        users = {}

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


# ________________MESSAGE HANDLING________________]
def get_username(conn):
    ip_address = conn.getpeername()
    return logged_users[ip_address]


def create_random_question(username):
    global questions
    global users

    while True:
        question_id, question_data = random.choice(list(questions.items()))
        if question_id not in users[username]["questions_asked"]:
            users[username]["questions_asked"].append(question_id)
            break
    question = question_data["question"]
    answers = '#'.join(question_data["answers"])

    question_str = f'{question_id}#{question}#{answers}'
    return question_str


def handle_question_msg(conn):
    username = get_username(conn)
    if len(users[username]["questions_asked"]) == len(questions):
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["no_question_msg"], '')
        return

    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["question_msg"], create_random_question(username))


def handle_answer_msg(conn, data):
    """
        Receives: socket
        Returns: None
        """
    global questions

    id, user_answer = data.split('#')
    correct_index = questions[id]["correct"]
    correct_answer = questions[id]["answers"][correct_index - 1]

    if correct_answer == questions[id]["answers"][int(user_answer) - 1]:
        username = get_username(conn)
        users[username]["score"] += 5
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["correct_answer_msg"], '')
    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["wrong_answer_msg"],
                               questions[id]["answers"][correct_index - 1])


def handle_logged_msg(conn):
    """
        Receives: socket
        Returns: None
        """
    global logged_users

    logged = [(address, username) for address, username in logged_users.items()]
    logged_string = ''.join(f'{index + 1}. {username}\n' for index, (address, username) in enumerate(logged))
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["logged_in_msg"], logged_string)


def handle_highscore_massage(conn):
    """
        Receives: socket
        Returns: None
        """
    global users

    users_scores = [(username, user["score"]) for username, user in users.items()]

    sorted_scores = sorted(users_scores, key=lambda x: x[1], reverse=True)

    string_scores = ''.join(f'{user} : {score}\n' for user, score in sorted_scores)

    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["highscore_msg"], string_scores)


def handle_getscore_message(conn):
    """
        Receives: socket
        Returns: None
        """
    global users

    ip_user = conn.getpeername()
    username = logged_users[ip_user]
    user_data = users.get(username)
    build_and_send_message(conn, chatlib.PROTOCOL_SERVER["user_score_msg"], str(user_data["score"]))


def handle_logout_message(conn):
    """
    Receives: socket
    Returns: None
    """
    global logged_users

    users[get_username(conn)]["questions_asked"].clear()
    logged_users.pop(conn.getpeername())

    conn.close()


def handle_login_message(conn, data):
    """
    Gets socket and message data of login message. Checks  user and pass exists and match.
    If not - sends error and finished. If all ok, sends OK message and adds user and address to logged_users
    Receives: socket, message code and data
    Returns: None (sends answer to client)
    """
    global users  # This is needed to access the same users.json dictionary from all functions
    global logged_users  # To be used later

    parts = data.split('#')
    username = parts[0]
    user = users.get(username)
    if user:
        if user["password"] == parts[1]:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_ok_msg"], '')
            # add to logged_users here
            ip_address = conn.getpeername()
            logged_users[ip_address] = username
        else:
            build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], '')

    else:
        build_and_send_message(conn, chatlib.PROTOCOL_SERVER["login_failed_msg"], '')

    save_user_database()  # Save changes to the user database


def save_user_database():
    with open("users.txt", "w") as file:
        for username, data in users.items():
            password = data["password"]
            score = data["score"]
            questions = ",".join(data["questions_asked"])
            file.write(f"{username}:{password}:{score}:{questions}\n")


def handle_client_message(conn, cmd, data):
    """
    Gets message code and data and calls the right function to handle command
    Receives: socket, message code and data
    Returns: None
    """
    global logged_users

    if conn.getpeername() not in logged_users.keys():
        if cmd == chatlib.PROTOCOL_CLIENT["login_msg"]:
            handle_login_message(conn, data)
        else:
            send_error(conn, "Wrong command")
    else:
        if cmd == chatlib.PROTOCOL_CLIENT["logout_msg"]:
            handle_logout_message(conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["score_msg"]:
            handle_getscore_message(conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["highscore_msg"]:
            handle_highscore_massage(conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["logged_in_users"]:
            handle_logged_msg(conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["question_msg"]:
            handle_question_msg(conn)
        elif cmd == chatlib.PROTOCOL_CLIENT["answer_msg"]:
            handle_answer_msg(conn, data)
        else:
            send_error(conn, ERROR_MSG)


def print_client_sockets(client_sockets):
    for c in client_sockets:
        print("\t", c.getpeername())


def main():
    # Initializes global users.json and questions.json dictionaries using load functions, will be used later
    global users
    global questions

    users = load_user_database()
    questions = load_questions()

    print("Welcome to Trivia Server!")
    server_socket = setup_socket()

    client_sockets = []
    # messages_to_send = []
    while True:
        client_sockets = [sock for sock in client_sockets if sock.fileno() != -1]
        try:
            ready_to_read, ready_to_write, in_error = select.select([server_socket] + client_sockets, client_sockets,
                                                                    [])
        except ValueError as e:
            print("ValueError in select:", e)
            print("client_sockets:", client_sockets)
            break
        for current_socket in ready_to_read[:]:
            if current_socket == server_socket:
                (client_socket, client_address) = server_socket.accept()
                print("New client Joined!")
                client_sockets.append(client_socket)
                print_client_sockets(client_sockets)
            else:
                print("New data from client")
                try:
                    cmd, data = recv_message_and_parse(current_socket)
                    if not cmd:
                        # The socket is closed
                        client_sockets.remove(current_socket)
                        print(f'Client {current_socket.getpeername()} disconnected.')
                        users[get_username(current_socket)]["questions_asked"].clear()
                        print_client_sockets(client_sockets)
                        continue

                    handle_client_message(current_socket, cmd, data)

                except (ConnectionResetError, ConnectionAbortedError):
                    # Handle the case where the client has disconnected
                    client_sockets.remove(current_socket)
                    print(f'Client {current_socket.getpeername()} disconnected.')
                    current_socket.close()
                    print_client_sockets(client_sockets)

            answer_clients(ready_to_write)


if __name__ == '__main__':
    main()
