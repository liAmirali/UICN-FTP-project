import socket

from .constants import SERVER_ROOT

class FTPState:
    def __init__(self):
        self.server_dir: str = SERVER_ROOT
        self.user: str | None = None
        self.data_sock: socket.socket | None = None

    def cd(self, dir):
        self.server_dir = dir