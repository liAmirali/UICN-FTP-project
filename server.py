import socket

INTERFACE_HOST = "localhost"
INTERFACE_CTRL_PORT = 2021
INTERFACE_DATA_PORT = 2020

class State:
    def __init__(self):
        self.dir: str = "/"
        self.user: str | None = None

    def cd(self, dir):
        self.dir = dir
    



def main():
    ftp_state = State()

    ctrl_s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    ctrl_s.bind((INTERFACE_HOST, INTERFACE_CTRL_PORT))
    ctrl_s.listen(5)

    print(f"Server is listening on http://{INTERFACE_HOST}:{INTERFACE_CTRL_PORT}")

    client_socket, client_address = ctrl_s.accept()

    while True:
        input_cmd = client_socket.recv(1024).decode()
        print("IN CMD:", input_cmd)

        client_socket.sendall("OK 200".encode())
        

        # if input_cmd
    

if __name__ == "__main__":
    main()