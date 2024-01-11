import socket
import ssl
import os

from .constants import *
from config import SERVER_CERT, SERVER_KEY


def create_data_conn():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(SERVER_CERT, SERVER_KEY)

    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_sock.bind((INTERFACE_HOST, INTERFACE_DATA_PORT))
    data_sock.listen(1)

    secure_server_socket = context.wrap_socket(data_sock, server_side=True)

    response_message = f"""227 Entering Passive Mode ({','.join(INTERFACE_HOST.split('.'))},{
        INTERFACE_DATA_PORT >> 8},{INTERFACE_DATA_PORT & 255})."""

    return response_message, secure_server_socket


def send_file(data_sock: socket.socket, file_path: str):
    data_conn, client_data_addr = data_sock.accept()

    print("---BEGIN SEND---")
    with open(file_path, "r", encoding="utf-8") as f:
        data_conn.send(bytes(os.path.basename(file_path), encoding="utf-8"))

        data_conn.send(bytes(f.read(), encoding="utf-8"))

    data_conn.close()


def recv_file(data_sock: socket.socket):
    data_conn, client_data_addr = data_sock.accept()

    print("CONNECTION ACCEPTED")

    file_addr = data_conn.recv(1024).decode("utf-8")
    print(f"{file_addr=} RECEIVED")

    file_data = data_conn.recv(1024 * 1024).decode("utf-8")
    print(f"{file_data=} RECEIVED")

    with open(file_addr, "w") as file:
        file.write(file_data)

    data_conn.close()
