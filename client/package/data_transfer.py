import socket
import ssl
import re
import os

from config import SERVER_CERT


def extract_passive_res(response):
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

        return ip_address, port
    else:
        print("No match found.")

        return None, None



def recv_file(data_ip, data_port):
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(SERVER_CERT)

    print("---BEGIN RECV---")
    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        data_sock.connect((data_ip, data_port))
    except Exception as exp:
        print("Couldn't connect to data socket")
        return

    secure_data_socket = context.wrap_socket(data_sock, server_hostname=data_ip)

    file_name = secure_data_socket.recv(1024).decode("utf-8")
    print(f"{file_name=} RECEIVED")

    file_data = secure_data_socket.recv(1024 * 1024).decode("utf-8")
    print(f"{file_data=} RECEIVED")

    with open(file_name, "w") as file:
        file.write(file_data)

    print("---WRITE DONE---")

    secure_data_socket.close()


def send_file(data_ip, data_port, file_path_client, file_path_server):
    context = ssl.create_default_context(ssl.Purpose.SERVER_AUTH)
    context.load_verify_locations(SERVER_CERT)

    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        data_sock.connect((data_ip, data_port))
    except Exception as exp:
        print("Couldn't connect to data socket")
        return
    
    secure_data_socket = context.wrap_socket(data_sock, server_hostname=data_ip)

    with open(file_path_client, "r") as f:
        file_addr = file_path_server + '/' + os.path.basename(file_path_client)
        file_data = f.read()

        secure_data_socket.send(bytes(file_addr, encoding="utf-8"))

        secure_data_socket.send(bytes(file_data, encoding="utf-8"))

    secure_data_socket.close()


def initiate_passive_mode(ctrl_conn: socket.socket):
    ctrl_conn.send(bytes("PASV", encoding="utf-8"))
    res = ctrl_conn.recv(1024).decode()
    print("PASV command Response:", res)
    ip, port = extract_passive_res(res)

    print(f"Server data port is {port}, and  IP is {ip}")

    return ip, port
