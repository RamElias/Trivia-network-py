import socket
import time

import chatlib  # To use chatlib functions or consts, use chatlib.****

SERVER_IP = "127.0.0.1"  # Our server will run on same computer as client
SERVER_PORT = 5678


# HELPER SOCKET METHODS

def build_and_send_message(conn, code, data):
    """
    Builds a new message using chatlib, wanted code and message.
    Prints debug info, then sends it to the given socket.
    Paramaters: conn (socket object), code (str), data (str)
    Returns: Nothing
    """
    full_msg = chatlib.build_message(code, data)
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
    cmd, data = chatlib.parse_message(full_msg)
    return cmd, data


def connect():
    my_socket = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    my_socket.connect((SERVER_IP, SERVER_PORT))
    return my_socket


def error_and_exit(error_msg):
    print(f'Error: {error_msg}')
    exit(1)


def login(conn):
    while True:
        username = input("------- Hello! -------\nPlease enter username: ")
        password = input("Please enter your password: ")
        cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["login_msg"], f'{username}#{password}')
        if cmd == chatlib.PROTOCOL_SERVER["login_ok_msg"]:
            return True
        else:
            print("Login failed, wrong user name or password..\n")
            return False


def logout(conn):
    build_and_send_message(conn, chatlib.PROTOCOL_CLIENT["logout_msg"], "")


def build_send_recv_parse(conn, cmd, data):
    build_and_send_message(conn, cmd, data)
    return recv_message_and_parse(conn)


def get_score(conn):
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["score_msg"], "")
    print(f'-----------------------------\n'
          f'Your score is: {data} points\n'
          f'-----------------------------')


def get_highscore(conn):
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["highscore_msg"], "")
    print(f'-----------------------------\n'
          f'High score table:\n-user-|-score-\n{data}'
          f'-----------------------------')


def get_logged_users(conn):
    cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["logged_in_users"], "")
    print(f"\nLogged users:\n{data}")


def play_question(conn):
    que_cmd = ''
    while que_cmd != 'n':
        cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["question_msg"], "")
        if data == '':
            print(f"------------------------------\n"
                  "No more Question! Well played!\n"
                  "------------------------------")
            break

        question = data.split('#')
        answer_id = question[0]
        print(f'  Q: {question[1]}\n'
              f'     1. {question[2]}\n'
              f'     2. {question[3]}\n'
              f'     3. {question[4]}\n'
              f'     4. {question[5]}')
        answer = input("Please choose yout choice[1-4]: ")
        cmd, data = build_send_recv_parse(conn, chatlib.PROTOCOL_CLIENT["answer_msg"], f'{answer_id}#{answer}')
        if data == '':
            print(f"------------------------------\n"
                  "Correct answer, well done!\n"
                  "------------------------------")
        else:
            print(f"------------------------------\n"
                  "Wrong, correct answer is: {data}\n"
                  "------------------------------")

        while True:
            que_cmd = input("Next Question? [y/n] \n")
            if que_cmd == 'y' or 'n':
                break


def main():
    while True:
        client_socket = connect()
        if login(client_socket):
            print("logged in!")
            while True:
                print("p   Play a trivia question\n"
                      "s   Get my score\n"
                      "h   get high score\n"
                      "l   get logged users\n"
                      "q   quit")
                cmd = input("Please Enter your choice: ")
                if cmd == 'p':
                    play_question(client_socket)
                elif cmd == 's':
                    get_score(client_socket)
                elif cmd == 'h':
                    get_highscore(client_socket)
                elif cmd == 'l':
                    get_logged_users(client_socket)
                elif cmd == 'q':
                    logout(client_socket)
                    print("Goodbye!")
                    break
                else:
                    print("Wrong command")


if __name__ == '__main__':
    main()
