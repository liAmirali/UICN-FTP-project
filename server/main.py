import socket
import ssl
import os
import threading

from package.constants import *
from access_config import USERS
from package.utils import parse_cmd, check_valid_path, is_accessible, update_history, get_history
from package.data_transfer import create_data_conn, send_file, recv_file
from package.FTPState import FTPState
from config import SERVER_CERT, SERVER_KEY


def run(cs: socket.socket, state: FTPState):
    input_cmd = cs.recv(1024).decode()
    input_cmd.strip()

    if input_cmd == "":
        return

    print("Incoming Command:", input_cmd)

    update_history(command=input_cmd, user=state.user)

    # Parsing user input
    args = parse_cmd(input_cmd)
    instr = args[0]

    os.chdir(state.absdir)

    if state.authenticated and state.user:
        is_accessible(args, state.user)

    res = "200 OK"

    if instr == "USER":
        res = "403 User does not exist."
        for u in USERS:
            if u["username"] == args[1]:
                state.user = args[1]
                state.authenticated = False
                res = "200 User found."
                break
    elif instr == "PASS":
        res = "403 User does not exists"
        for u in USERS:
            if u["username"] == state.user:
                if u["password"] == args[1]:
                    res = "200 Authenticated."
                    state.authenticated = True
                    break
                else:
                    res = "403 Wrong password."
        if res.split(" ")[0] != "200":
            state.user = None
            state.authenticated = False

    elif instr == "LIST":
        file_list = os.listdir(args[1])
        print(f"{file_list=}")

        res = ""
        for f in file_list:
            res += f + "  "
    elif instr == "CWD":
        if not check_valid_path(args[1]):
            return "422 Invalid path"
        state.cd(args[1])
    elif instr == "CDUP":
        state.cd("..")
    elif instr == "PASV":
        res, data_sock = create_data_conn()
        state.data_sock = data_sock
    elif instr == "RETR":
        if not os.path.isfile(args[1]):
            return "422 Not a file."

        if not state.data_sock:
            return "404 A data connection is not initiated."

        send_file_thread = threading.Thread(
            target=send_file, args=(state.data_sock, args[1]))

        send_file_thread.start()
        send_file_thread.join()

        if state.data_sock:
            state.data_sock.close()
            state.data_sock = None
        res = "200 File sent successfully."
    elif instr == "STOR":
        if not os.path.exists(args[2]):
            return "422 Path not found on server."

        if not state.data_sock:
            return "404 A data connection is not initiated."

        recv_file_thread = threading.Thread(
            target=recv_file, args=(state.data_sock,))

        recv_file_thread.start()
        recv_file_thread.join()

        if state.data_sock:
            state.data_sock.close()
            state.data_sock = None
        res = "200 File sent successfully."
    elif instr == "DELE":
        if not os.path.isfile(args[1]):
            return "404 File does not exist."

        os.remove(args[1])

    elif instr == "MKD":
        os.makedirs(args[1])
        res = "200 Path created."
    elif instr == "RMD":
        if not os.path.exists(args[1]):
            return "404 Directory does not exists."

        if not os.path.isdir(args[1]):
            return "422 Path is not a directory."

        if os.listdir(args[1]):
            return "422 Directory not empty."

        os.rmdir(args[1])
    elif instr == "PWD":
        res = state.absdir
    elif instr == "QUIT":
        if state.data_sock:
            state.data_sock.close()

        res = "221 QUITTED"
    elif instr == "REPORT":
        if state.user == "admin":
            history = get_history()
            res = history
        else:
            res = "403 Forbidden."

    return res


def handle_new_client(ctrl_s: socket.socket, client_socket: socket.socket):
    ftp_state = FTPState()

    while True:
        try:
            old_dir = os.getcwd()

            res = run(client_socket, ftp_state)

            client_socket.sendall(bytes(res, encoding="utf-8"))

            if res == "221 QUITTED":
                ctrl_s.close()
                break
        except Exception as exp:
            print("Error:", exp)
            if ftp_state.data_sock:
                ftp_state.data_sock.close()

            client_socket.sendall(bytes(str(exp), encoding="utf-8"))
        finally:
            os.chdir(old_dir)


def main():
    context = ssl.create_default_context(ssl.Purpose.CLIENT_AUTH)
    context.load_cert_chain(SERVER_CERT, SERVER_KEY)

    ctrl_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ctrl_s.bind((INTERFACE_HOST, INTERFACE_CTRL_PORT))
    ctrl_s.listen(5)

    # Wrapping our socket with SSL
    secure_server_socket = context.wrap_socket(ctrl_s, server_side=True)

    print(
        f"Server is listening on http://{INTERFACE_HOST}:{INTERFACE_CTRL_PORT}")

    while True:
        client_socket, client_address = secure_server_socket.accept()

        print(f"A new client is connected. Address={client_address}")

        new_client_thread = threading.Thread(
            target=handle_new_client, args=(secure_server_socket, client_socket))
        new_client_thread.start()


if __name__ == "__main__":
    main()
