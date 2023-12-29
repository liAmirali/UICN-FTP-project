import socket
import os
import threading


# TODO: Create config file
INTERFACE_HOST = "127.0.0.1"
INTERFACE_CTRL_PORT = 6921
INTERFACE_DATA_PORT = 6920

SERVER_ROOT = "/"

VALID_CMDS = {
    "PASV": {"argc": 1},
    "USER": {"argc": 2},
    "PASS": {"argc": 2},
    "LIST": {"argc": 2},
    "RETR": {"argc": 2},
    "STOR": {"argc": 3},
    "DELE": {"argc": 2},
    "MKD": {"argc": 2},
    "RMD": {"argc": 2},
    "CWD": {"argc": 2},
    "CDUP": {"argc": 1},
    "QUIT": {"argc": 1}
}


class FTPState:
    def __init__(self):
        self.server_dir: str = SERVER_ROOT
        self.user: str | None = None
        self.data_sock: socket.socket | None = None

    def cd(self, dir):
        self.server_dir = dir


def create_data_conn():
    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    data_sock.bind((INTERFACE_HOST, INTERFACE_DATA_PORT))
    data_sock.listen(1)

    response_message = f"""227 Entering Passive Mode ({','.join(INTERFACE_HOST.split('.'))},{
        INTERFACE_DATA_PORT >> 8},{INTERFACE_DATA_PORT & 255})."""

    print("response_message:", response_message)

    return response_message, data_sock


def check_valid_path(path):
    try:
        return bool(os.path.exists(path))
    except OSError:
        return False


def parse_cmd(cmd):
    args = cmd.split(" ")
    instr = args[0]

    if instr in VALID_CMDS:
        argc = VALID_CMDS[instr]["argc"]
        print("ARGC: ", argc)

        if argc == len(args):
            return args

        raise Exception("422 Invalid arg count")

    raise Exception("422 Invalid command")


def send_file(data_sock: socket.socket, file_path: str):
    data_conn, client_data_addr = data_sock.accept()
    
    print("---BEGIN SEND---")
    with open(file_path, "r", encoding="utf-8") as f:
        data_conn.send(bytes(os.path.basename(file_path), encoding="utf-8"))

        print("AFTER SEND FILE NAME")

        data_conn.send(bytes(f.read(), encoding="utf-8"))
        print("AFTER SEND FILE DATA")

    data_conn.close()


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
        res = "200 File sent successfully."

    return res


def main():
    ftp_state = FTPState()

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
