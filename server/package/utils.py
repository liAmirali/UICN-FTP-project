import os

from .constants import VALID_CMDS
from access_config import USERS, PRIVATE_PATHS


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

        if argc == len(args):
            return args

        raise Exception("422 Invalid arg count")

    raise Exception("422 Invalid command")


def path_satisfy(server_path, client_path):
    if os.path.isdir(server_path):
        if os.path.isdir(client_path) or os.path.isfile(client_path):
            server_path_abs = os.path.abspath(server_path)
            client_path_abs = os.path.abspath(client_path)
            return client_path_abs.startswith(server_path_abs)

    elif os.path.isfile(server_path):
        if os.path.isdir(client_path):
            return False
        elif os.path.isfile(client_path):
            server_path_abs = os.path.abspath(server_path)
            client_path_abs = os.path.abspath(client_path)
            return client_path_abs == server_path_abs

    return False


def is_accessible(args, user):
    for u in USERS:
        if u["username"] == user and u["is_privilaged"]:
            return

    for server_arg in VALID_CMDS[args[0]]["srv_args"]:
        for path in PRIVATE_PATHS:
            if path_satisfy(path, args[server_arg]):
                raise Exception("You cannot access this path.")
