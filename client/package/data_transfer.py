import socket
import re
import os


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


def recv_file(data_ip, data_port):
    print("---BEGIN RECV---")
    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        data_sock.connect((data_ip, data_port))
    except Exception as exp:
        print("Couldn't connect to data socket")
        return

    file_name = data_sock.recv(1024).decode("utf-8")
    print(f"{file_name=} RECEIVED")

    file_data = data_sock.recv(1024 * 1024).decode("utf-8")
    print(f"{file_data=} RECEIVED")

    with open(file_name, "w") as file:
        file.write(file_data)

    print("WRITE DONE")

    data_sock.close()


def send_file(data_ip, data_port, file_path_client, file_path_server):
    data_sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        data_sock.connect((data_ip, data_port))
    except Exception as exp:
        print("Couldn't connect to data socket")
        return

    with open(file_path_client, "r") as f:
        file_addr = file_path_server + '/' + os.path.basename(file_path_client)
        file_data = f.read()

        data_sock.send(bytes(file_addr, encoding="utf-8"))

        print("AFTER SEND FILE NAME")

        data_sock.send(bytes(file_data, encoding="utf-8"))
        print("AFTER SEND FILE DATA")

    data_sock.close()


def initiate_passive_mode(ctrl_conn: socket.socket):
    ctrl_conn.send(bytes("PASV", encoding="utf-8"))
    res = ctrl_conn.recv(1024).decode()
    ip, port = extract_passive_res(res)

    print(f"SERVER DATA PORT IS {port}, IP: {ip}")

    return ip, port
