# -*- coding: utf-8 -*-


import socket, pickle, tqdm, os, time, threading, re


"""
status code
10: response Header
20: response File
"""

class Server():
    def __init__(self, max_listening=1):
        self.host = '0.0.0.0'
        self.port = 7777

        self.file_name = None
        self.file_location = None

        self.max_listening = max_listening # max waiting count
        self.chunk_size = 4096
        self.users = {}


    def init(self):
        if not self.file_name or not self.file_location : raise SystemError('Uninitialized file')

        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.server.listen(self.max_listening)
        return print('---Successfully Initialized Server---')


    def startListening(self):
        print(f'server start listening {self.server.getsockname()[0]}:{self.server.getsockname()[1]}...')
        while True:
            client, client_address = self.server.accept()
            self.users[client_address] = client
            print(f'Client connect successful {self.users[client_address].getpeername()[0]}:{self.users[client_address].getpeername()[1]}')

            thread = threading.Thread(target=self.waitingSend, args=(self.users[client_address], client_address), daemon=True)
            thread.start()


    def waitingSend(self, client, client_address):
        while True:
            try:
                client.settimeout(5)
                package = client.recv(self.chunk_size)
                status = pickle.loads(package)
                print(status)
            except:
                client.close()
                self.users.pop(client_address)
                return print(f"Close connect client {client_address}")

            client.settimeout(None)
            #print(f'users: {self.showUser()}')
            if status['code'] == 10 : self.sendHeader(client)
            elif status['code'] == 20 : self.sendFile(client)
            """
            else:
                try:
                    status = { 'code' : 412 }
                    package = pickle.dumps(status)
                    client.sendall(package)
                except:
                    client.close()
                    self.users.pop(client_address)
                    return print(f"Close connection {client_address}")
            """


    def sendHeader(self, client):
        self.file_size = os.path.getsize(self.file_location) # get file size

        header = {
            'file_name' : self.file_name,
            'file_size' : self.file_size # bytes
        }
        
        print(header)
        package = pickle.dumps(header)

        try:
            client.sendall(package)
        except:
            return print("Fail to send header")

        return print('Send header successfully')


    def sendFile(self, client):
        with open(self.file_location, 'rb') as f:
            progress = tqdm.tqdm(range(int(self.file_size)), f'send{self.file_size}', unit='K', unit_divisor=1024)

            while True:
                bytes_read = f.read(self.chunk_size) # read file

                if not bytes_read:
                    return print("\n--All send successfully")

                try:
                    client.sendall(bytes_read)
                    progress.update(len(bytes_read))
                except :
                    self.connection = False
                    return print("\nClient close connection")

    def stop(self):
        self.connection = False
        print("***Close server***")
        return exit(0)


    def setHost(self, host, port):
        self.host = host
        self.port = port
        return


    def setFile(self, filelocation):
        self.file_location = filelocation
        self.file_name = getFilename(filelocation)
        return


    def showUser(self):
        return self.users




def getFilename(file_addr):
    split_file = re.split('\/',file_addr)
    return split_file[len(split_file)-1]




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