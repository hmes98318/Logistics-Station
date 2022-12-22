# -*- coding: utf-8 -*-

import socket, pickle, os, time, threading, re, pathlib


"""
status code
10: response Header
20: response File
"""
SERVER = 'Server:'


class Server():
    def __init__(self, max_listening=1):
        self.host = '0.0.0.0'
        self.port = 7777

        self.max_listening = max_listening  # max waiting count
        self.chunk_size = 4096
        self.users = {}

        self.file_location = None
        self.file_name = None
        self.file_type = None


    def init(self):
        if not self.file_name or not self.file_location: raise SystemError(SERVER, 'Uninitialized file.')

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        print(SERVER, 'Successfully Initialized Server.')
        return True


    def startListening(self):
        self.server.listen(self.max_listening)
        print(SERVER, f'Server start listening {self.server.getsockname()[0]}:{self.server.getsockname()[1]}...')
        while True:
            try:
                client, client_address = self.server.accept()
                self.users[client_address] = client
                print(SERVER, f'Client connect successful {self.users[client_address].getpeername()[0]}:{self.users[client_address].getpeername()[1]}')

                thread = threading.Thread(target=self.waitingSend, args=(self.users[client_address], client_address),
                                          daemon=True)
                thread.start()
            except:
                print(SERVER, '***Stop listening***')
                return False


    def waitingSend(self, client, client_address):
        while True:
            try:
                client.settimeout(5)
                package = client.recv(self.chunk_size)
                status = pickle.loads(package)
                print(SERVER, f'status = {str(status)}')
            except:
                client.close()
                self.users.pop(client_address)
                print(SERVER, f"Close connect client {client_address}")
                return False

            client.settimeout(None)
            # print(SERVER, f'users: {self.showUser()}')
            if status['code'] == 10:
                self.sendHeader(client)
            elif status['code'] == 20:
                self.sendFile(client)


    def sendHeader(self, client):

        header = {
            'file_name': self.file_name,
            'file_size': self.file_size,  # bytes
            'file_type': self.file_type  # .txt
        }

        print(SERVER, f'header = {str(header)}')
        package = pickle.dumps(header)

        try:
            client.sendall(package)
        except:
            print(SERVER, '--Fail to send header.')
            return False

        print(SERVER, 'Send header successfully.')
        return True


    def sendFile(self, client):
        with open(self.file_location, 'rb') as f:
            while True:
                bytes_read = f.read(self.chunk_size)  # read file

                if not bytes_read:
                    print(SERVER, 'All send successfully.')
                    return True

                try:
                    client.sendall(bytes_read)
                except:
                    print(SERVER, '--Client stop connection.')
                    return False


    def stop(self):
        self.server.close()
        print(SERVER, '***Close server***')
        return True


    def setHost(self, host, port):
        self.host = host
        self.port = port
        return True


    def setFile(self, filelocation):
        self.file_location = filelocation

        self.file_name = pathlib.Path(self.file_location).name  # get file name
        self.file_size = os.path.getsize(self.file_location)  # get file size
        self.file_type = ''.join(pathlib.Path(self.file_location).suffixes)  # ['.tar', 'gz'] => '.tar.gz'
        return True


    def showUser(self):
        return self.users


"""
if __name__ == '__main__':
    server_host = '192.168.31.146'#'0.0.0.0'#'127.0.0.1'#
    server_port = 7777
    server_filelocation = './tmp/01.txt'

    server = Server()
    server.setHost(server_host, server_port)
    server.setFile(server_filelocation)
    server.init()
    server.startListening()
    #server.stop()
"""
