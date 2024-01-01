import socket
import os
import threading

from package.constants import *
from package.utils import parse_cmd, check_valid_path
from package.data_transfer import create_data_conn, send_file, recv_file
from package.FTPState import FTPState

ftp_state = FTPState()


def run(cs: socket.socket, state: FTPState):
    input_cmd = cs.recv(1024).decode()
    print("IN CMD:", input_cmd)

    # Parsing user input
    args = parse_cmd(input_cmd)
    instr = args[0]

    res = "200 OK"

    if instr == "LIST":
        # TODO: Specify directory or file for the client
        file_list = os.listdir(args[1])
        print(f"{file_list=}")

        res = ""
        for f in file_list:
            res += f + "  "
    elif instr == "CWD":
        # TODO: Specify directory or file for the client
        if not check_valid_path(args[1]):
            return "422 Invalid path"
        state.cd(args[1])
        os.chdir(args[1])
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
        print("IN STOR IF")
        if not os.path.exists(args[2]):
            return "422 Path not found on server."

        if not state.data_sock:
            return "404 A data connection is not initiated."

        print("TO EXE THREAD")

        recv_file_thread = threading.Thread(
            target=recv_file, args=(state.data_sock,))

        recv_file_thread.start()
        recv_file_thread.join()

        if state.data_sock:
            state.data_sock.close()
            state.data_sock = None
        res = "200 File sent successfully."

    return res


def main():
    ctrl_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ctrl_s.bind((INTERFACE_HOST, INTERFACE_CTRL_PORT))
    ctrl_s.listen(5)

    print(
        f"Server is listening on http://{INTERFACE_HOST}:{INTERFACE_CTRL_PORT}")

    client_socket, client_address = ctrl_s.accept()

    while True:
        try:
            res = run(client_socket, ftp_state)
            client_socket.sendall(bytes(res, encoding="utf-8"))
        except Exception as exp:
            print("ERR :((", exp)
            client_socket.sendall(bytes(str(exp), encoding="utf-8"))


if __name__ == "__main__":
    main()
