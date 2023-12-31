import re

from .constants import VALID_CMDS

def check_path_format(path):
    # Regular expression for Unix-like paths (absolute or relative)
    unix_path_pattern = r'^(/|\.\.?/|[\w\s\.-]+/[\w\s\.-]+)*$'

    # Regular expression for Windows-like paths (absolute or relative)
    windows_path_pattern = r'^([a-zA-Z]:\\|\\\\[\w\s\.-]+\\[\w\s\.-]+)*$'

    if re.match(unix_path_pattern, path):
        # "Unix-like path format detected."
        return True
    elif re.match(windows_path_pattern, path):
        # "Windows-like path format detected."
        return True
    else:
        # "Unknown path format."
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