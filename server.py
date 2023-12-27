import socket
import os


# TODO: Create config file
INTERFACE_HOST = "localhost"
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


def check_valid_path(path):
    if os.name == 'nt':  # Windows path
        try:
            # Checking if the path is valid for Windows
            return bool(os.path.exists(path))
        except OSError:
            return False
    else:  # Linux or Unix path
        return os.path.isabs(path)


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


def run(cs, state):
    input_cmd = cs.recv(1024).decode()
    print("IN CMD:", input_cmd)

    # Parsing user input
    try:
        args = parse_cmd(input_cmd)
        instr = args[0]
    except Exception as exp:
        cs.sendall(exp)
        return

    print(f"{args=}")
    print(f"{instr=}")

    res = ""

    if instr == "LIST":
        # TODO: Specify directory or file for the client
        file_list = os.listdir(args[1])
        print(f"{file_list=}")

        for f in file_list:
            res += f + "  "
    elif instr == "CWD":
        # TODO: Specify directory or file for the client
        if not check_valid_path(args[1]):
            cs.sendall("422 Invalid path")
            return
        state.cd(args[1])

    cs.sendall(bytes(res).encode())


def main():
    ftp_state = State()

    ctrl_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ctrl_s.bind((INTERFACE_HOST, INTERFACE_CTRL_PORT))
    ctrl_s.listen(5)

    print(
        f"Server is listening on http://{INTERFACE_HOST}:{INTERFACE_CTRL_PORT}")

    client_socket, client_address = ctrl_s.accept()

    try:
        while True:
            run(client_socket, ftp_state)
    except Exception as exp:
        print("ERR :((", exp)


if __name__ == "__main__":
    main()
