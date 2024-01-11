import socket
import ssl
import threading

from package.constants import *
from package.data_transfer import initiate_passive_mode, recv_file, send_file
from package.utils import parse_cmd


def run(client_s: socket.socket):
    cmd = input("Enter your command: ")

    args = parse_cmd(cmd)

    if args[0] == "RETR" or args[0] == "STOR":
        data_ip, data_port = initiate_passive_mode(client_s)

        client_s.send(bytes(cmd, encoding='utf-8'))

        if args[0] == "RETR":
            recv_file_thread = threading.Thread(
                target=recv_file, args=(data_ip, data_port))
            recv_file_thread.start()

        elif args[0] == "STOR":
            recv_file_thread = threading.Thread(
                target=send_file, args=(data_ip, data_port, args[1], args[2]))
            recv_file_thread.start()
    elif args[0] == "DELE":
        confirmationRes = input("Do you really wish to delete? (Y/N) ")
        if confirmationRes == "Y":
            client_s.send(bytes(cmd, encoding='utf-8'))
        else:
            return "File deletion not confirmed."

    else:
        client_s.send(bytes(cmd, encoding='utf-8'))

    reply = client_s.recv(1024 * 1024).decode()

    return reply


def authenticate_user(client_s: socket.socket):
    username = input("Enter your username: ")
    cmd = f"USER {username}"
    client_s.send(bytes(cmd, encoding='utf-8'))
    reply = client_s.recv(1024).decode()

    print("Reply:", reply)
    if reply.split(" ")[0] != "200":
        return False

    password = input("Enter your password: ")
    cmd = f"PASS {password}"
    client_s.send(bytes(cmd, encoding='utf-8'))
    reply = client_s.recv(1024).decode()

    print("Reply:", reply)
    if reply.split(" ")[0] != "200":
        return False

    return True


def main():
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations("../server_cert.pem")

    client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)


    # server_host, server_port = input("Enter the server post and host (example: 127.0.0.1:20): ").split(":")
    server_host, server_port = DUMMY_HOST, DUMMY_CTRL_PORT

    server_port = int(server_port)

    try:
        client_s.connect((server_host, server_port))
    except Exception as exp:
        print(f"Error: Couldn't connect to the server. {exp}")
        return

    # Wrap the socket with SSL
    secure_client_socket = context.wrap_socket(client_s, server_hostname=DUMMY_HOST)

    try:
        authenticated = authenticate_user(secure_client_socket)
        if not authenticated:
            secure_client_socket.close()
            return
    except Exception as exp:
        print("Error:", exp)
        secure_client_socket.close()
        return

    while True:
        try:
            reply = run(secure_client_socket)
            print("Reply:", reply)

            if reply == "221 QUITTED":
                secure_client_socket.close()
                break

        except Exception as exp:
            print("Error:", exp)


if __name__ == "__main__":
    main()
