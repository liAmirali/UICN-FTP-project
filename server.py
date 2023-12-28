import socket
import os


# TODO: Create config file
INTERFACE_HOST = "127.0.0.1"
INTERFACE_CTRL_PORT = 2021
INTERFACE_DATA_PORT = 2020

SERVER_ROOT = "/"

VALID_CMDS = {
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


class State:
    def __init__(self):
        self.server_dir: str = SERVER_ROOT
        self.user: str | None = None

    def cd(self, dir):
        self.server_dir = dir


def create_data_conn():
    file_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    file_conn.bind((INTERFACE_HOST, INTERFACE_DATA_PORT))
    file_conn.listen(1)

    response_message = f"""227 Entering Passive Mode ({','.join(INTERFACE_HOST.split('.'))},{
        INTERFACE_DATA_PORT >> 8},{INTERFACE_DATA_PORT & 255})."""
    return response_message


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


def send_file(data_conn: socket.socket, file_path: str):
    with open(file_path, "r", encoding="utf-8") as f:
        data_conn.sendall(bytes(f.name, encoding="utf-8"))
        data_conn.sendall(bytes(f.read(), encoding="utf-8"))

    data_conn.close()


def run(cs, state):
    input_cmd = cs.recv(1024).decode()
    print("IN CMD:", input_cmd)

    # Parsing user input
    args = parse_cmd(input_cmd)
    instr = args[0]

    print(f"{args=}")
    print(f"{instr=}")

    res = "200 OK"

    data_conn: socket.socket | None = None

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
        data_conn = create_data_conn()
    elif instr == "RETR":
        if not os.path.isfile(args[1]):
            return "422 Not a file."

        if not data_conn:
            return "404 A data connection is not initiated."

        send_file(data_conn, args[1])
        res = "200 File sent successfully."

    return res


def main():
    ftp_state = State()

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
