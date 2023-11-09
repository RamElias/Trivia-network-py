# Protocol Constants

CMD_FIELD_LENGTH = 16  # Exact length of cmd field (in bytes)
LENGTH_FIELD_LENGTH = 4  # Exact length of length field (in bytes)
MAX_DATA_LENGTH = 10 ** LENGTH_FIELD_LENGTH - 1  # Max size of data field according to protocol
MSG_HEADER_LENGTH = CMD_FIELD_LENGTH + 1 + LENGTH_FIELD_LENGTH + 1  # Exact size of header (CMD+LENGTH fields)
MAX_MSG_LENGTH = MSG_HEADER_LENGTH + MAX_DATA_LENGTH  # Max size of total message
DELIMITER = "|"  # Delimiter character in protocol
DATA_DELIMITER = "#"  # Delimiter in the data part of the message

# Protocol Messages 
# In this dictionary we will have all the client and server command names

PROTOCOL_CLIENT = {
    "login_msg": "LOGIN",
    "logout_msg": "LOGOUT",
    "score_msg": "MY_SCORE",
    "highscore_msg": "HIGHSCORE",
    "logged_in_users": "LOGGED",
    "question_msg": "GET_QUESTION",
    "answer_msg": "SEND_ANSWER"
}

PROTOCOL_SERVER = {
    "login_ok_msg": "LOGIN_OK",
    "login_failed_msg": "ERROR"
}  # ..  Add more commands if needed

# Other constants

ERROR_RETURN = None  # What is returned in case of an error


def build_message(cmd, data):
    """
    Gets command name (str) and data field (str) and creates a valid protocol message
    Returns: str, or None if error occured
    """
    if cmd not in PROTOCOL_CLIENT.values() and cmd not in PROTOCOL_SERVER.values():
        return None

    cmd += ' ' * (CMD_FIELD_LENGTH - len(cmd))
    data_length = str(len(data)).zfill(LENGTH_FIELD_LENGTH)

    return f'{cmd}{DELIMITER}{data_length}{DELIMITER}{data}'


def parse_message(data):
    """
    Parses protocol message and returns command name and data field
    Returns: cmd (str), data (str). If some error occured, returns None, None
    """
    data = data.split(DELIMITER)
    if len(data) < 2:
        return None, None

    cmd = data[0].strip()

    try:
        data_length = int(data[1])
    except ValueError:
        return None, None

    if not (0 <= data_length <= 9999):
        return None, None

    # if len(data) == 3:
    msg = data[2]
    if data_length != len(msg):
        return None, None

    return cmd, msg


def split_data(msg, expected_fields):
    """
    Helper method. gets a string and number of expected fields in it. Splits the string
    using protocol's data field delimiter (|#) and validates that there are correct number of fields.
    Returns: list of fields if all ok. If some error occured, returns None
    """
    arr = msg.split(DATA_DELIMITER)
    if len(arr) == expected_fields + 1:
        return arr

    return None


def join_data(msg_fields):
    """
    Helper method. Gets a list, joins all of it's fields to one string divided by the data delimiter.
    Returns: string that looks like cell1#cell2#cell3
    """
    str_fields = [str(field) for field in msg_fields]
    return DATA_DELIMITER.join(str_fields)

# print(join_data(["username", "password"]))
# print(join_data(["question", "ans1", "ans2", "ans3", "ans4", "correct"]))
# print(build_message("LOGIN", "aaa#bbb"))
# print(parse_message("LOGIN           |0011|aaa#bbbbbbb"))
