import socket

def main():
    client_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)

    server_host, server_port = input("Enter the server post and host (example: 127.0.0.1:20): ").split(":")
    server_port = int(server_port)

    try:
        client_s.connect((server_host, server_port))
    except Exception as exp:
        print("ERR: Couldn't connect to the server.")
        return
        

    while True:
        cmd = input("Enter your command: ")
        
        client_s.send(bytes(cmd, encoding='utf-8'))
        print(f"SENT: {cmd}")

        reply = client_s.recv(1024).decode()
        print(f"REPLY: {reply}")
    

if __name__ == "__main__":
    main()