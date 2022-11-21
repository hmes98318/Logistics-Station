# -*- coding: utf-8 -*-


import socket, pickle, tqdm, os, time


"""
status code
10: require Header
20: require File
"""

class Client():
    def __init__(self):
        self.host = None
        self.port = 7777

        self.save_folder = None
        self.file_name = 'received_file'

        self.file_size = None
        self.chunk_size = 4096
        self.connection = False


    def start(self):
        if not self.host : raise SystemError('Unset host.')
        if not self.save_folder : raise SystemError('Unset save folder.')

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f'start connecting {self.host}:{self.port}')

        retry = 0
        while True:
            try:
                self.client.connect((self.host, self.port))
            except:
                if retry > 3: 
                    self.connection = False
                    print('Fail to connect')
                    return False
                retry += 1
                print('Fail to connect, try again')
                time.sleep(1)
                pass

            self.connection = True
            print(f'Connect to server successfully {self.client.getpeername()[0]}:{self.client.getpeername()[1]}')
            return True


    def askHeader(self):
        if not self.connection : raise SystemError('Server not connection.')

        status = { 'code' : 10 }
        package = pickle.dumps(status)

        try: # Ask header
            self.client.sendall(package)
        except:
            print('Fail to send')
            return True

        try: # Receive header
            self.client.settimeout(5)
            received_package = self.client.recv(self.chunk_size)
        except:
            self.connection = False
            self.stop()
            print('Fail to receive package')
            return False

        self.client.settimeout(None)
        header = pickle.loads(received_package)
        print(header)

        self.file_name = header['file_name']
        self.file_size = header['file_size']
        return True


    def askFile(self):
        if not self.connection : raise SystemError('Server not connection.')
        if not self.file_size : raise SystemError('Fail to get header, retry askHeader().')

        status = { 'code' : 20 }
        package = pickle.dumps(status)

        try: # Ask file
            self.client.sendall(package)
        except:
            print('Fail to send')
            return False

        # start receive file
        print('Start receive file')
        file_location = f'{self.save_folder}/received_{getTime()}_{self.file_name}'
        with open(file_location, 'wb') as f:
            progress = tqdm.tqdm(range(int(self.file_size)), f'receive {self.file_name}', unit='K', unit_divisor=1024, unit_scale=True)

            received_size = 0
            self.client.settimeout(1)
            while not received_size == self.file_size:
                try:
                    bytes_read = self.client.recv(self.chunk_size) # read data from server
                except:
                    self.connection = False
                    print('\nFail to get file')
                    return False

                f.write(bytes_read)
                progress.update(len(bytes_read))
                received_size += len(bytes_read)

            self.stop()
            print("\n--All file received")
            return True


    def stop(self):
        self.connection = False
        self.client.close()
        print("***Close connection***")
        return True


    def setHost(self, host, port):
        self.host = host
        self.port = port
        return True


    def setFolder(self, save_folder):
        save_folder = save_folder.replace('\\\\','/') # .\\save -> ./save

        if not isDir(save_folder) :
            try:
                os.makedirs(save_folder)
                print('Save folder not exist, create new one.')
            except:
                print('Save folder not exist, failed to create new one.')
                return False

        self.save_folder = save_folder
        return True


    def showConnection(self):
        return self.connection




def getTime():
    localtime = time.localtime()
    result = time.strftime("%I-%M-%S", localtime)
    return str(result)


def isDir(folder):
    return os.path.isdir(folder)



"""
if __name__ == '__main__':
    server_host = '192.168.31.146'#'127.0.0.1'#
    server_port = 7777
    save_folder = 'C:/Users/usr/Desktop/p2py/save'#'C:\\Users\\usr\\Desktop\\p2py' #'./save'

    client = Client()
    client.setHost(server_host, server_port)
    client.setFolder(save_folder)

    client.start()
    client.askHeader()
    time.sleep(1)
    print(f'connection: {client.showConnection()}')
    time.sleep(1)
    client.askFile()
    client.stop()
    print(f'connection: {client.showConnection()}')
"""