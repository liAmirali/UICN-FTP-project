import socket
import os


class FTPState:
    def __init__(self):
        self.user: str | None = None
        self.authenticated: bool = False
        self.data_sock: socket.socket | None = None
        self.absdir: str = "/home/elnayu/University/5/CN/project/phase02"

    def cd(self, path):
        os.chdir(path)
        new_wd = os.getcwd()
        self.absdir = new_wd
