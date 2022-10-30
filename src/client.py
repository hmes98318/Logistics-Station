# -*- coding: utf-8 -*-


import socket, pickle, tqdm, os, time

"""
client:
// startConnect()
// askHeader()
// recvFile()
// stopConnect()
"""

class Client():
    def __init__(self, host, port, save_folder, file_location='./', file_name='', file_size=0, chunk_size=4096, connection=False):
        self.host = host
        self.port = port
        
        self.save_folder = save_folder
        self.file_location = file_location
        self.file_name = file_name
        self.file_size = file_size
        self.chunk_size = chunk_size
        self.connection = connection

    def start(self):
        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f'start connecting {self.host}:{self.port}')

        retry = 0
        while not self.connection:
            try:
                self.client.connect((self.host, self.port))
                self.connection = True
                print(f'Connect to server successfully {self.client.getpeername()[0]}:{self.client.getpeername()[1]}')
                self.connection = True

            except:
                if retry > 4: 
                    self.connection = False
                    return print('Fail to connect')
                retry += 1
                print('Fail to connect, try again')
                pass

    def getHeader(self):
        retry = 0
        self.client.settimeout(5)
        while self.connection:
            try:
                receive = self.client.recv(self.chunk_size)
                break
            except:
                if retry > 4: 
                    self.connection = False
                    return print('Fail to getHeader')
                retry += 1
                print('Fail to getHeader, try again')
                pass

        self.client.settimeout(None)
        header = pickle.loads(receive)
        print(header)

        self.file_name = header['file_name']
        self.file_size = header['file_size']

        if not self.receivedResponse():
            self.connection = False
            return print('Fail to response')
        return
    
    def getFile(self):
        self.file_location = f'{self.save_folder}/received_{getTime()}_{self.file_name}'

        with open(self.file_location, 'wb') as f:
            progress = tqdm.tqdm(range(int(self.file_size)), f'receive {self.file_name}', unit='K', unit_divisor=1024, unit_scale=True)

            received_size = 0
            self.client.settimeout(1)
            while not received_size == self.file_size:
                try:
                    bytes_read = self.client.recv(self.chunk_size) # read data from server
                except:
                    self.connection = False
                    return print('\nFail to get file')

                f.write(bytes_read)
                progress.update(len(bytes_read))
                received_size += len(bytes_read)

            return print("\n--all file received")


    def receivedResponse(self):
        response = 'RECEIVED'
        package = pickle.dumps(response)
        try:
            self.client.sendall(package)
        except:
            print('Fail to send response')
            self.connection = False
            return False
        return True

    def stop(self):
        self.connection = False
        self.client.close()
        return print("close connection")







def getTime():
    localtime = time.localtime()
    result = time.strftime("%I-%M-%S", localtime)
    return str(result)








"""
if __name__ == '__main__':
    server_host = '127.0.0.1'#'192.168.31.146'
    server_port = 7777
    save_folder = './save'

    client = Client(server_host, server_port, save_folder)
    client.start()
    client.getHeader()
    client.getFile()
"""