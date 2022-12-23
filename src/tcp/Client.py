# -*- coding: utf-8 -*-

import socket, pickle, os, time


"""
status code
10: require Header
20: require File
"""
CLIENT = 'Client:'


class Client():
    def __init__(self):
        self.host = None
        self.port = 7777

        self.chunk_size = 4096
        self.connection = False

        self.save_folder = None
        self.file_name = 'received_file'
        self.file_size = None
        self.file_type = 'txt'
        self.progress = 0


    def start(self):
        if not self.host : raise SystemError(CLIENT, 'Host not set.')
        if not self.save_folder : raise SystemError(CLIENT, 'Save folder not set.')

        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(CLIENT, f'Start connecting {self.host}:{self.port}')

        retry = 0
        while True:
            try:
                self.client.connect((self.host, self.port))
                break
            except:
                if retry >= 3: 
                    self.connection = False
                    print(CLIENT, '--Fail to connect.')
                    return False
                retry += 1
                print(CLIENT, '--Fail to connect, try again.')
                time.sleep(1)
                pass

        self.connection = True
        print(CLIENT, f'Connect to server successfully {self.client.getpeername()[0]}:{self.client.getpeername()[1]}')
        return True


    def askHeader(self):
        if not self.connection : raise SystemError(CLIENT, 'Server not connection.')

        status = { 'code' : 10 }
        package = pickle.dumps(status)

        try: # Ask header
            self.client.sendall(package)
        except:
            print(CLIENT, '--Fail to send.')
            return True

        try: # Receive header
            self.client.settimeout(5)
            received_package = self.client.recv(self.chunk_size)
        except:
            self.connection = False
            self.stop()
            print(CLIENT, '--Fail to receive package.')
            return False

        self.client.settimeout(None)
        header = pickle.loads(received_package)
        print(CLIENT, f'header = {str(header)}')

        self.file_name = header['file_name']
        self.file_size = header['file_size']
        self.file_type = header['file_type']
        self.progress = 0 # clear download progress
        return True


    def askFile(self, ProgressBarUpdate):
        if not self.connection : raise SystemError(CLIENT, 'Server not connection.')
        if not self.file_size : raise SystemError(CLIENT, 'Fail to get header, retry askHeader().')

        status = { 'code' : 20 }
        package = pickle.dumps(status)

        try: # Ask file
            self.client.sendall(package)
        except:
            print(CLIENT, '--Fail to send askFile()')
            return False

        # start receive file
        print(CLIENT, 'Start receive file.')
        self.progress = 0 # clear download progress

        file_location = f'{self.save_folder}/received_{getTime()}_{self.file_name}'
        with open(file_location, 'wb') as f:

            received_size = 0
            self.client.settimeout(1)
            while not received_size == self.file_size:
                try:
                    bytes_read = self.client.recv(self.chunk_size) # read data from server
                except:
                    self.connection = False
                    print(CLIENT, '--Fail to receive file.')
                    return False

                f.write(bytes_read)
                received_size += len(bytes_read)
                self.progress = countProgress(received_size, self.file_size)
                ProgressBarUpdate.emit()

            self.stop()
            print(CLIENT, 'All file received.')
            return True


    def stop(self):
        self.connection = False
        self.client.close()
        print(CLIENT, '***Close connection***')
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
                print(CLIENT, 'Save folder not exist, create new one.')
            except:
                print(CLIENT, '--Save folder not exist, failed to create new one.')
                return False

        self.save_folder = save_folder
        return True


    def showConnection(self):
        return self.connection
    
    def showProgress(self):
        return self.progress
    
    def showFilename(self):
        return self.file_name

    def showFilesize(self):
        return self.file_size
    
    def showFiletype(self):
        return self.file_type




def countProgress(a, b):
    percentage = 100 * float(a) / float(b)
    return int(percentage)


def getTime():
    localtime = time.localtime()
    result = time.strftime('%I-%M-%S', localtime)
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