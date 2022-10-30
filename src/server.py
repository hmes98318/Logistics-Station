# -*- coding: utf-8 -*-


import socket, pickle, tqdm, os, time

"""
server:
packageFile()
// startServer()
// sendHeader()
// sendFile()
// stopServer()
"""

class Server():
    def __init__(self, host, port, file_name, file_location, max_listening=1, chunk_size=4096, connection=False):
        self.host = host
        self.port = port

        self.file_name = file_name
        self.file_location = file_location

        self.max_listening = max_listening
        self.chunk_size = chunk_size
        self.connection = connection


    def start(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(self.max_listening)
        print(f'server start listening {self.server.getsockname()[0]}:{self.server.getsockname()[1]}')

        self.client, client_address = self.server.accept()
        print(f'client connection success {self.client.getpeername()[0]}:{self.client.getpeername()[1]}')
        self.connection = True
        return

    def sendHeader(self):
        if not self.connection:
            return print('Client not connect.')

        self.file_size = os.path.getsize(self.file_location) # get file size

        header = {
            'file_name' : self.file_name,
            'file_size' : self.file_size # bytes
        }

        print(header)
        package = pickle.dumps(header)
        try:
            self.client.sendall(package)
        except:
            self.connection = False
            return print("Fail to send header")

        print('send header successfully')

        if not self.waitReceive():
            self.connection = False
            return print('Client disconnect')
        return

    def sendFile(self):
        if not self.connection:
            return print('Client not connect.')

        with open(self.file_location, 'rb') as f:
            progress = tqdm.tqdm(range(int(self.file_size)), f'send{self.file_size}', unit='K', unit_divisor=1024)

            while True:
                bytes_read = f.read(self.chunk_size) # read file

                if not bytes_read:
                    self.stop()
                    return print("\n--all send successfully")

                try:
                    self.client.sendall(bytes_read)
                    progress.update(len(bytes_read))
                except :
                    self.connection = False
                    return print("\nclient close connection")
                

    def waitReceive(self):
        retry = 0
        while self.connection:
            try:
                self.client.settimeout(5)
                data = self.client.recv(self.chunk_size)
                if pickle.loads(data) == 'RECEIVED':
                    print('Client received data')
                    self.client.settimeout(None)
                    return True
            except:
                print('--retry')
                if retry > 4: 
                    self.client.settimeout(None)
                    self.connection = False
                    return False
                retry += 1

    def stop(self):
        self.connection = False
        self.client.close()
        return print("close connection")

    def status(self):
        if not self.connection:
            return print('Client not connect.')

        print(f'server working on {self.server.getsockname()[0]}:{self.server.getsockname()[1]}')
        

"""
if __name__ == '__main__':
    server_host = '192.168.31.146'#'0.0.0.0'#'127.0.0.1'#
    server_port = 7777
    server_filename = '01.txt'
    server_filelocation = './tmp/test.7z'

    server = Server(server_host, server_port, server_filename, server_filelocation)
    
    while True:
        server.start()
        #time.sleep(8)
        server.status()
        server.sendHeader()
        server.sendFile()
        server.stop()
"""