import socket

class FTPState:
    def __init__(self):
        self.user: str | None = None
        self.authenticated: bool = False
        self.data_sock: socket.socket | None = None