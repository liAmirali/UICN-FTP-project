import socket
import threading

from package.constants import *
from package.data_transfer import initiate_passive_mode, recv_file
from package.utils import parse_cmd


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
