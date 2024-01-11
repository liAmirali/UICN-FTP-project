DUMMY_HOST = "127.0.0.1"
DUMMY_CTRL_PORT = 6921
INTERFACE_DATA_PORT = 3020

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
    "PWD": {"argc": 1},
    "CDUP": {"argc": 1},
    "QUIT": {"argc": 1}
}