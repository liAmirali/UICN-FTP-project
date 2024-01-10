import socket
import os


class FTPState:
    def __init__(self):
        self.user: str | None = None
        self.authenticated: bool = False
        self.data_sock: socket.socket | None = None
        self.absdir: str = "/"

    def cd(self, path):
        os.chdir(path)
        new_wd = os.getcwd()
        self.absdir = new_wd
