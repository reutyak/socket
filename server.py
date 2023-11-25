import socket
import select
counter = 0
MSG_LEN_BYTE = 2
NICK_NAME_LEN_BYTE = 2
ROOM_NAME_LEN_BYTE = 2

# Local variables
rooms = [{"room name": "lobby", "password": "", "clients": [], "nick_names": []},
         {"room name": "", "password": "", "clients": [], "nick_names": []},
         {"room name": "", "password": "", "clients": [], "nick_names": []},
         {"room name": "", "password": "", "clients": [], "nick_names": []},
         {"room name": "", "password": "", "clients": [], "nick_names": []},
         {"room name": "", "password": "", "clients": [], "nick_names": []},
         {"room name": "", "password": "", "clients": [], "nick_names": []},
         {"room name": "", "password": "", "clients": [], "nick_names": []},
         {"room name": "", "password": "", "clients": [], "nick_names": []},
         {"room name": "", "password": "", "clients": [], "nick_names": []}]
socket_list = []
client_list = []


def broadcastMsg(msg, room_name, nick, client):
    msg_len = len(nick) + 2 + 2 + len(room_name) + len(msg)
    if msg_len < 10:
        msg_len = "0{}".format(msg_len)
    else:
        pass
    if len(nick) == 10:
        nick_len = "10"
    else:
        nick_len = "0{}".format(len(nick))
    if len(room_name) > 10:
        room_name_len = len(room_name)
    else:
        room_name_len = "0{}".format(len(room_name))
    msg_to_send = "{}{}{}{}{}{}{}".format(1, msg_len, room_name_len,  nick_len, room_name, nick, msg)
    for room in rooms:
        if room["room name"] == room_name:
            for clientA in room["clients"]:
                if clientA is not client:
                    clientA.send(msg_to_send.encode())
                else:
                    continue
        else:
            continue


def answer(num, msg, client):
    msg_len = 2 + len(room_name) + len(msg)
    if msg_len < 10:
        msg_len = "0{}".format(msg_len)
    if len(room_name) > 10:
        room_name_len = len(room_name)
    else:
        room_name_len = "0{}".format(len(room_name))
    msg_to_send = "{}{}{}{}{}".format(num, msg_len, room_name_len, room_name, msg)
    client.send(msg_to_send.encode())


sock_server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
sock_server.bind(("127.0.0.1", 8087))
sock_server.listen(3)

socket_list.append(sock_server)

while True:
    # waiting for messages..
    read_ready, _, _ = select.select(socket_list, [], [])
    for i in read_ready:
        if i is sock_server:
            # Server accepting new clients
            client, addr = sock_server.accept()
            socket_list.append(client)
            client_list.append(client)
        else:
            # Message from client handler
            msg_type = int(i.recv(1).decode())

            if msg_type == 1:
                nick_name_len = int(i.recv(2).decode())
                nick_name = i.recv(nick_name_len).decode()
                rooms[0]["clients"].append(i)
                rooms[0]["nick_names"].append(nick_name)
            if msg_type == 2:
                msg_len = int(i.recv(2).decode())
                room_name_len = int(i.recv(2).decode())
                nick_name_len = int(i.recv(2).decode())
                room_name = i.recv(room_name_len).decode()
                client_nick_name = i.recv(nick_name_len).decode()
                msg = "False"
                for room in rooms:
                    try:
                        if room["room name"] == room_name:
                            room["clients"].append(i)
                            room["nick_names"].append(client_nick_name)
                            msg = "True"
                            broadcastMsg("I joined the room", room_name, client_nick_name, i)
                            break
                        else:
                            continue
                    except:
                        pass
                msg_len = ROOM_NAME_LEN_BYTE + len(room_name) + len(msg)
                if len(room_name) > 10:
                    room_name_len = len(room_name)
                else:
                    room_name_len = "0{}".format(len(room_name))
                i.send("{}{}{}{}{}".format(2, msg_len, room_name_len, room_name, msg).encode())
                continue
            if msg_type == 3:
                msg_len = int(i.recv(2).decode())
                room_name_len = int(i.recv(2).decode())
                nick_name_len = int(i.recv(2).decode())
                room_name = i.recv(room_name_len).decode()
                client_nick_name = i.recv(nick_name_len).decode()
                for room in rooms:
                    try:
                        if room["room name"] == room_name:
                            room["clients"].remove(i)
                            room["nick_names"].remove(client_nick_name)
                            broadcastMsg("I left the room", room_name, client_nick_name, i)
                            continue
                    except:
                        pass
            if msg_type == 4:
                msg_len = int(i.recv(2).decode())
                room_name_len = int(i.recv(2).decode())
                password_len = int(i.recv(1).decode())
                room_name = i.recv(room_name_len).decode()
                password = i.recv(password_len).decode()
                result = "False"
                for room in rooms:
                    if room["room name"] == "":
                        room["room name"] = room_name
                        room["password"] = password
                        result = "True"
                        break
                    else:
                        continue
                if result == "True":
                    answer(3, "True", i)
                else:
                    answer(3, "False", i)

            if msg_type == 5:
                msg_len = int(i.recv(2).decode())
                room_name_len = int(i.recv(2).decode())
                password_len = int(i.recv(1).decode())
                room_name = i.recv(room_name_len).decode()
                password = i.recv(password_len).decode()
                for room in rooms:
                    if room["room name"] == room_name and room["password"] == password:
                        msg = "{} room closed, type exit and transfer to the lobby".format(room_name)
                        broadcastMsg(msg, room_name, "group manager", i)
                        room["room name"] = ""
                        room["password"] = ""
                        room["clients"] = []
                        room["nick_names"] = []
                        break
                    else:
                        continue
                    continue
                continue
            if msg_type == 6:
                msg_len = int(i.recv(2).decode())
                room_name_len = int(i.recv(2).decode())
                nick_name_len = int(i.recv(2).decode())
                room_name = i.recv(room_name_len).decode()
                nick_name = i.recv(nick_name_len).decode()
                msg = i.recv(msg_len - 2 - 2 - room_name_len - nick_name_len).decode()
                broadcastMsg(msg, room_name, nick_name, i)
            if msg_type == 7:
                msg_len = int(i.recv(2).decode())
                room_name_len = int(i.recv(2).decode())
                room_name = i.recv(room_name_len).decode()
                msg = ""
                for room in rooms:
                    try:
                        if room["room name"] == room_name:
                            for nick in room["nick_names"]:
                                msg += (nick + ", ")
                                continue
                    except:
                        pass
                msg_len2 = ROOM_NAME_LEN_BYTE + len(room_name) + len(msg)
                if len(room_name) > 10:
                    room_name_len = len(room_name)
                else:
                    room_name_len = "0{}".format(len(room_name))
                if msg_len2 < 10:
                    msg_len2 = "0{}".format(msg_len2)
                else:
                    pass
                i.send("{}{}{}{}{}".format(5, msg_len2, room_name_len, room_name, msg).encode())
            if msg_type == 8:
                    msg = ""
                    for room in rooms:
                        if room["room name"] != "":
                            msg += (room["room name"]+", ")
                    msg_len = len(str(msg))
                    if msg_len < 10:
                        msg_len = "0{}".format(msg_len)
                    else:
                        pass
                    msg_to_send = "{}{}{}".format(4, msg_len, msg)
                    i.send(msg_to_send.encode())





