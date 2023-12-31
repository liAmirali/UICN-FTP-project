import socket
import os

from .constants import *


def create_data_conn():
    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_sock.bind((INTERFACE_HOST, INTERFACE_DATA_PORT))
    data_sock.listen(1)

    response_message = f"""227 Entering Passive Mode ({','.join(INTERFACE_HOST.split('.'))},{
        INTERFACE_DATA_PORT >> 8},{INTERFACE_DATA_PORT & 255})."""

    print("response_message:", response_message)

    return response_message, data_sock


def send_file(data_sock: socket.socket, file_path: str):
    data_conn, client_data_addr = data_sock.accept()

    print("---BEGIN SEND---")
    with open(file_path, "r", encoding="utf-8") as f:
        data_conn.send(bytes(os.path.basename(file_path), encoding="utf-8"))

        print("AFTER SEND FILE NAME")

        data_conn.send(bytes(f.read(), encoding="utf-8"))
        print("AFTER SEND FILE DATA")

    data_conn.close()

def recv_file(data_sock: socket.socket):
    data_conn, client_data_addr = data_sock.accept()

    file_name = data_conn.recv(1024).decode("utf-8")
    print(f"{file_name=} RECVED")

    file_data = data_conn.recv(1024 * 1024).decode("utf-8")
    print(f"{file_data=} RECVED")

    with open(file_name, "w") as file:
        file.write(file_data)


