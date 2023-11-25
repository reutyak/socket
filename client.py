import socket
import threading

# local variables
sock_client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_client.connect(("127.0.0.1", 8087))
MSG_TYPE_LEN_BYTE = 1
MSG_LEN_BYTE = 2
NICK_NAME_LEN_BYTE = 2
ROOM_NAME_LEN_BYTE = 2
PASSWORD_LEN_BYTE = 1
connection = False


def login(sock, nick_name):
    if len(nick_name) == 10:
        new_nick_name_len = "10"
    else:
        new_nick_name_len = "0{}".format(len(nick_name))
    sock.send("{}{}{}".format(1, new_nick_name_len, nick_name).encode())


def create_delete_room(sock, num, room_name, password):
    this_msg_len = len(password)+len(room_name)+PASSWORD_LEN_BYTE+ROOM_NAME_LEN_BYTE
    if this_msg_len < 10:
        this_msg_len = "0{}".format(this_msg_len)
    if len(room_name) > 10:
        this_room_name_len = len(room_name)
    else:
        this_room_name_len = "0{}".format(len(room_name))
    sock.send("{}{}{}{}{}{}".format(num, this_msg_len, this_room_name_len, len(password), room_name, password).encode())


def send_msg(sock, room_name, nick_name):
    while True:
        msg_to_send = input("Typing the word exit will return you to the main menu\nEnter message to send: ")
        if msg_to_send == "exit":
            room_name_len = len(room_name)
            if room_name_len < 10:
                room_name_len = "0{}".format(room_name_len)
            else:
                room_name_len = len(my_room_name)
            if len(nick_name) == 10:
                nick_name_len = len(nick_name)
            else:
                nick_name_len = "0{}".format(len(nick_name))
                msg_len = len(room_name) + len(nick_name) + ROOM_NAME_LEN_BYTE + NICK_NAME_LEN_BYTE
                sock_client.send("{}{}{}{}{}{}".format
                                 (3, msg_len, room_name_len, nick_name_len, room_name, nick_name)
                                 .encode())
                break
        your_msg_len = len(msg_to_send) +ROOM_NAME_LEN_BYTE + NICK_NAME_LEN_BYTE +len(room_name) + len(nick_name)
        if len(nick_name) == 10:
            your_nick_name_len = "10"
        else:
            your_nick_name_len = "0{}".format(len(nick_name))
        if len(room_name) > 10:
            your_room_name_len = len(room_name)
        else:
            your_room_name_len = "0{}".format(len(room_name))
        sock.send("{}{}{}{}{}{}{}".format(6, your_msg_len, your_room_name_len, your_nick_name_len, room_name,  nick_name, msg_to_send).encode())

def receive():
    # message receive handler
    while True:
        try:
            msg_type_re = int(sock_client.recv(MSG_TYPE_LEN_BYTE).decode())
        except ValueError:
            break
        if msg_type_re == 1:
            try:
                msg_len_re = int(sock_client.recv(MSG_LEN_BYTE).decode())
                room_name_len_re = int(sock_client.recv(2).decode())
                nick_name_len_re = int(sock_client.recv(NICK_NAME_LEN_BYTE).decode())
                room_name_re = sock_client.recv(room_name_len_re).decode()
                nick_name_re = sock_client.recv(nick_name_len_re).decode()
                msg_re = sock_client.recv(msg_len_re - ROOM_NAME_LEN_BYTE - NICK_NAME_LEN_BYTE
                                - room_name_len_re - nick_name_len_re).decode()
                print("room name: {} \n {} : {}".format(room_name_re, nick_name_re, msg_re))
            except ValueError:
                print("Failed to receive message")
        if msg_type_re == 2:
            try:
                msg_len_re = int(sock_client.recv(MSG_LEN_BYTE).decode())
                room_name_len_re = int(sock_client.recv(ROOM_NAME_LEN_BYTE).decode())
                room_name_re = sock_client.recv(room_name_len_re).decode()
                msg_re = sock_client.recv(msg_len_re - ROOM_NAME_LEN_BYTE - room_name_len_re).decode()
                if msg_re == "False":
                    print("Enter to the room failed")
                    break
                if msg_re == "True":
                    print("Enter to {} room was successfully made".format(room_name_re))
                    continue
                else:
                    print("error")
                    break
            except ValueError:
                break
        if msg_type_re == 3:
            try:
                msg_len_re = int(sock_client.recv(MSG_LEN_BYTE).decode())
                room_name_len_re = int(sock_client.recv(ROOM_NAME_LEN_BYTE).decode())
                room_name_re = sock_client.recv(room_name_len_re).decode()
                msg_re = sock_client.recv(msg_len_re - ROOM_NAME_LEN_BYTE - room_name_len_re).decode()
                if not msg_re:
                    print("Creating the room failed")
                if msg_re:
                    print("Creating {} room was successfully made".format(room_name_re))
                else:
                    print("error")
            except ValueError:
                break
            continue
        if msg_type_re == 4:
            msg_len_re = int(sock_client.recv(MSG_LEN_BYTE).decode())
            msg_re = sock_client.recv(msg_len_re).decode()
            print("The open rooms are:\n {}".format(msg_re))
        if msg_type_re == 5:
            try:
                msg_len_re = int(sock_client.recv(MSG_LEN_BYTE).decode())
                room_name_len_re = int(sock_client.recv(2).decode())
                room_name_re = sock_client.recv(room_name_len_re).decode()
                msg_re = sock_client.recv(msg_len_re - ROOM_NAME_LEN_BYTE - room_name_len_re).decode()
                print("The people in {} room: {}".format(room_name_re, msg_re))
            except ValueError:
                print("error")
            continue



thread_receive_msg = threading.Thread(target=receive)
thread_receive_msg.start()
# thread_send_msg = threading.Thread(target=send_msg)
# thread_send_msg.start()

# Login
while True:
    client_nick_name = input("Enter your nick name")
    if len(client_nick_name) > 10:
        print("Nick name is limited to 10 characters")
        continue
    else:
        while True:
            user_input = -1
            while True:
                print(
                    "Please make your choice and press Enter:\n"
                    "1)Entrance to the lobby\n"
                    "2)Creating a private room\n"
                    "3)Deleting a room\n"
                    "4)Entrance to a private room\n"
                    "5)List of private rooms\n"
                    "6)Room information")
                try:
                    user_input = int(input())
                except ValueError:
                    print("Wrong tapping, try again")
                    continue
                if 1 <= user_input <= 6:
                    break
                else:
                    print("Wrong tapping, try again")
                    continue
            if user_input == 1:
                login(sock_client, client_nick_name)
                connection = True
                send_msg(sock_client, "lobby", client_nick_name)
            if user_input == 2:
                if connection:
                    while True:
                        my_room_name = input("Enter name to the new room")
                        if len(my_room_name) > 20:
                            print("Room name is limited to 20 characters")
                            continue
                        else:
                            break
                    while True:
                        my_password = input("Enter password to the new room")
                        if len(my_password) > 8:
                            print("password is limited to 8 characters")
                            continue
                        else:
                            break
                    create_delete_room(sock_client, 4, my_room_name, my_password)
                    continue
                else:
                    print("Enter the lobby first to perform an initial login")
                    continue
            if user_input == 3:
                if connection:
                    while True:
                        my_room_name = input("Enter name of the room")
                        if len(my_room_name) > 20:
                            print("Room name is limited to 20 characters")
                            continue
                        else:
                            break
                    while True:
                        my_password = input("Enter password of the room")
                        if len(my_password) > 8:
                            print("password is limited to 8 characters")
                            continue
                        else:
                            break
                    create_delete_room(sock_client, 5, my_room_name, my_password)
                else:
                    print("Enter the lobby first to perform an initial login")
                    continue
            if user_input == 4:
                if connection:
                     while True:
                        my_room_name = input("Enter name the room")
                        if len(my_room_name) > 20:
                            print("Room name is limited to 20 characters")
                            break
                        else:
                            room_name_len = len(my_room_name)
                            if room_name_len < 10:
                                room_name_len = "0{}".format(room_name_len)
                            else:
                                room_name_len = len(my_room_name)
                            if len(client_nick_name) == 10:
                                nick_name_len = "10"
                            else:
                                nick_name_len = "0{}".format(len(client_nick_name))
                            msg_len = len(my_room_name)+len(client_nick_name) + ROOM_NAME_LEN_BYTE + NICK_NAME_LEN_BYTE
                            sock_client.send("{}{}{}{}{}{}".format
                                   (2, msg_len, room_name_len, nick_name_len, my_room_name, client_nick_name)
                                   .encode())
                        send_msg(sock_client, my_room_name, client_nick_name)
                        break
                else:
                    print("Enter the lobby first to perform an initial login")
                    break
                continue
            if user_input == 5:
                if connection:
                    sock_client.send("{}".format(8).encode())
                else:
                    print("Enter the lobby first to perform an initial login")
                    continue
            if user_input == 6:
                if connection:
                     while True:
                        my_room_name = input("Enter name the room")
                        if len(my_room_name) > 20:
                            print("Room name is limited to 20 characters")
                            break
                        else:
                            room_name_len = len(my_room_name)
                            if room_name_len < 10:
                                room_name_len = "0{}".format(room_name_len)
                            else:
                                pass
                            msg_len = len(my_room_name)+ ROOM_NAME_LEN_BYTE
                            if msg_len < 10:
                                msg_len = "0{}".format(msg_len)
                            else:
                                pass
                            sock_client.send("{}{}{}{}".format
                                   (7, msg_len, room_name_len, my_room_name)
                                   .encode())
                        break


