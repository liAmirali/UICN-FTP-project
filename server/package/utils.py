import os

from .constants import VALID_CMDS

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