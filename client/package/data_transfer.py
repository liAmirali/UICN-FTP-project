import socket
import re

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


def initiate_passive_mode(ctrl_conn: socket.socket) -> socket.socket:
    ctrl_conn.send(bytes("PASV", encoding="utf-8"))
    res = ctrl_conn.recv(1024).decode()
    ip, port = extract_passive_res(res)

    print(f"SERVER DATA PORT IS {port}, IP: {ip}")

    return ip, port
