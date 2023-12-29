import socket
import re
import threading


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
    "CDUP": {"argc": 1},
    "QUIT": {"argc": 1}
}


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


def initiate_passive_mode(ctrl_conn: socket.socket) -> socket.socket:
    ctrl_conn.send(bytes("PASV", encoding="utf-8"))
    res = ctrl_conn.recv(1024).decode()
    ip, port = extract_passive_res(res)

    print(f"SERVER DATA PORT IS {port}, IP: {ip}")

    return ip, port


def parse_cmd(cmd):
    args = cmd.split(" ")
    instr = args[0]

    if instr in VALID_CMDS:
        argc = VALID_CMDS[instr]["argc"]

        if argc == len(args):
            return args

        raise Exception("422 Invalid arg count")

    raise Exception("422 Invalid command")


def recv_file(data_ip: str, data_port: str):
    print("---BEGIN RECV---")
    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        data_sock.connect((data_ip, data_port))
    except Exception as exp:
        print("Couldn't connect to data socket")
        return

    file_name = data_sock.recv(1024).decode("utf-8")
    print(f"{file_name=} RECVED")

    file_data = data_sock.recv(1024 * 1024).decode("utf-8")
    print(f"{file_data=} RECVED")

    with open(file_name, "w") as file:
        file.write(file_data)
    
    print("WRITE DONE")


def extract_passive_res(response):
    print(response)
    # Sample response from PASV command
    # response = "227 Entering Passive Mode (127,0,0,1,12,34)."

    # Regular expression pattern to extract IP and port numbers
    pattern = r'\((?P<ip>[0-9,]+),(?P<p1>\d+),(?P<p2>\d+)\)'

    # Extracting IP address and port numbers using regex
    match = re.search(pattern, response)
    if match:
        ip_address = match.group('ip').replace(',', '.')
        port = (int(match.group('p1')) << 8) + int(match.group('p2'))
        print(f"IP Address: {ip_address}")
        print(f"Port: {port}")
    else:
        print("No match found.")

    return ip_address, port


def run(client_s: socket.socket):
    cmd = input("Enter your command: ")

    args = parse_cmd(cmd)

    if args[0] == "RETR" or args[0] == "STOR":
        data_ip, data_port = initiate_passive_mode(client_s)

        client_s.send(bytes(cmd, encoding='utf-8'))

        if args[0] == "RETR":
            print("IN RETR if")

            recv_file_thread = threading.Thread(target=recv_file, args=(data_ip, data_port))
            recv_file_thread.start()
            # recv_file(data_conn)
        elif args[0] == "STOR":
            pass
    else:
        client_s.send(bytes(cmd, encoding='utf-8'))

    reply = client_s.recv(1024 * 1024).decode()

    return reply


def main():
    client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    # server_host, server_port = input("Enter the server post and host (example: 127.0.0.1:20): ").split(":")
    server_host, server_port = DUMMY_HOST, DUMMY_CTRL_PORT

    server_port = int(server_port)

    try:
        client_s.connect((server_host, server_port))
    except Exception as exp:
        print(f"ERR: Couldn't connect to the server. {exp}")
        return

    while True:
        try:
            reply = run(client_s)
            print(f"REPLY: {reply}")
        except Exception as exp:
            print("ERR :(((((", exp)


if __name__ == "__main__":
    main()
