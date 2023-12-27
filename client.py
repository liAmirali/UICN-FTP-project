import socket
import re


DUMMY_HOST = "127.0.0.1"
DUMMY_CTRL_PORT = 2021
INTERFACE_DATA_PORT = 3020


def initiate_passive_mode(ctrl_conn: socket.socket) -> socket.socket:
    ctrl_conn.send(f"PASV")
    res = ctrl_conn.recv(1024).decode()
    ip, port = extract_passive_res(res)

    print(f"SERVER DATA PORT IS {port}, IP: {ip}")

    data_conn = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    try:
        data_conn.connect((ip, port))
    except Exception as exp:
        msg = f"ERR: Couldn't initiate the data connection. {exp}"
        data_conn.close()
        raise Exception(msg)
    

    return data_conn

def recv_file(data_conn):
    file_name = data_conn.recv(1024).decode("utf-8")
    file_data = data_conn.recv(1024 * 1024).decode("utf-8")

    with open(file_name, "w") as file:
        file.write(file_data)


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
    else:
        print("No match found.")

    return ip_address, port


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
        cmd = input("Enter your command: ")

        if cmd == "RETR" or cmd == "STOR":
            initiate_passive_mode()


        client_s.send(bytes(cmd, encoding='utf-8'))
        print(f"SENT: {cmd}")

        reply = client_s.recv(1024).decode()
        print(f"REPLY: {reply}")


if __name__ == "__main__":
    main()
