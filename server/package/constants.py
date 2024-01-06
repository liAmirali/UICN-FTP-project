INTERFACE_HOST = "127.0.0.1"
INTERFACE_CTRL_PORT = 6921
INTERFACE_DATA_PORT = 6920

VALID_CMDS = {
    "PASV": {"argc": 1, "srv_args": []},
    "USER": {"argc": 2, "srv_args": []},
    "PASS": {"argc": 2, "srv_args": []},
    "LIST": {"argc": 2, "srv_args": [1]},
    "RETR": {"argc": 2, "srv_args": [1]},
    "STOR": {"argc": 3, "srv_args": [2]},
    "DELE": {"argc": 2, "srv_args": [1]},
    "MKD": {"argc": 2, "srv_args": [1]},
    "RMD": {"argc": 2, "srv_args": [1]},
    "CWD": {"argc": 2, "srv_args": [1]},
    "PWD": {"argc": 1, "srv_args": []},
    "CDUP": {"argc": 1, "srv_args": []},
    "QUIT": {"argc": 1, "srv_args": []}
}
