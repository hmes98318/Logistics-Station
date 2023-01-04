import socket, json, os, time, pathlib, tarfile


"""
# Status Code

Client 100 : 檢查連接
Server 200: 連接成功

Client 110: 發送寄件請求
Server 111: 寄件成功(server res) 回傳 取件碼
Server 114: 寄件失敗(server error)

Client 120: 發送尋找包裹請求(req header)
Server 121: 回傳包裹資訊(server res) 回傳 header
Client 122: 開始取件(download)
Server 123: 查無包裹(server res)
Server 124: 取件失敗(server error)
Server 125: 取件成功(server res)
"""


class Client():
    def __init__(self):
        self.host = None
        self.port = 7000

        self.chunk_size = 1024
        self.connection = False
        self.packaged = False

        self.file_location = None
        self.file_name = 'send_file'
        self.file_size = 0
        self.file_type = '.txt'
        self.tar_size = 0
        self.upload_progress = 0
        # self.uploadList = {} # 暫時沒用到

        self.save_folder = './save'
        self.box_name = None
        self.box_size = None
        self.box_file_size = None # 解 tar 後的大小
        self.box_type = None
        self.download_progress = 0
        #self.downloadList = {} # 暫時沒用到

        self.cache_tar_upload = './tar-cache/upload' # 上傳跟下載 tar 的暫存位置
        self.cache_tar_download = './tar-cache/download'




    def setHost(self, host, port):
        self.host = socket.gethostbyname(host)
        self.port = port
        return True


    def setFile(self, file_location):
        file_location = file_location.replace('\\\\','/') # .\\file -> ./file
        self.file_location = file_location

        if isFile(file_location):
            self.file_name = (pathlib.Path(self.file_location).name).replace(''.join(pathlib.Path(self.file_location).suffixes), '')  # get file name
            self.file_size = os.path.getsize(self.file_location)  # get file size
            self.file_type = ''.join(pathlib.Path(self.file_location).suffixes)  # ['.tar', 'gz'] => '.tar.gz'
        else:
            self.file_name = pathlib.Path(self.file_location).name  # get folder name
            self.file_size = get_folder_size(self.file_location)  # get folder size
            self.file_type = '.dir' # set folder type
        return True


    def setSaveFolder(self, save_folder):
        save_folder = save_folder.replace('\\\\','/') # .\\save -> ./save

        if not isDir(save_folder) :
            try:
                os.makedirs(save_folder)
                print('Save folder not exist, create new one.')
            except:
                print('--Save folder not exist, failed to create new one.')
                return False

        self.save_folder = save_folder
        return True




    def start(self):
        if not self.host : raise SystemError('Host not set.')

        if not os.path.isdir(self.cache_tar_upload) :
            print('cache_upload folder not exist, create new one.')
            try:
                os.makedirs(self.cache_tar_upload)
            except:
                raise SystemError('--Permission denied, failed to create cache folder = ', self.cache_tar_upload)

        if not os.path.isdir(self.cache_tar_download) :
            print('cache_download folder not exist, create new one.')
            try:
                os.makedirs(self.cache_tar_download)
            except:
                raise SystemError('--Permission denied, failed to create cache folder = ', self.cache_tar_download)


        self.client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        print(f'Start connecting {self.host}:{self.port}')

        retry = 0
        while True:
            try:
                self.client.connect((self.host, self.port))
                break
            except:
                if retry >= 3: 
                    print('--Fail to connect.')
                    self.connection = False
                    return False
                print('--Fail to connect, try again.')
                retry += 1
                time.sleep(1)
                pass

        print(f'Connect to server successfully {self.client.getpeername()[0]}:{self.client.getpeername()[1]}')
        self.connection = True
        return True






    def reqConnection(self):
        print('Start checking connection status.')

        status = { 'code' : 100 }
        package = json.dumps(status).encode('UTF-8')

        try: # Ask header
            self.client.settimeout(5)
            self.client.sendall(package)
        except Exception as error:
            print('--reqConnection() Fail to send package to Server.')
            print(error)
            self.stop()
            self.connection = False
            return False

        try: # Receive connection Status
            received_package = self.client.recv(self.chunk_size)
        except:
            print('--Fail to receive Server Connection Status.')
            self.stop()
            self.connection = False
            return False

        self.client.settimeout(None)
        status = json.loads(received_package.decode('UTF-8'))

        code = status['code']
        print(f'Server connection status {code} ok.')
        self.connection = True
        return True


    def packingBox(self):
        print('Start packingBox().')
        SUCCESS_TAR_GENERATE = generateTar(self.file_name, self.file_location, self.cache_tar_upload)

        if SUCCESS_TAR_GENERATE:
            print('packingBox() succeed.')
            cache_file_location = f'{self.cache_tar_upload}/{self.file_name}.tar'
            self.tar_size = os.path.getsize(cache_file_location)
            self.packaged = True
            return True

        print('--packingBox() Failed.')
        return False


    def reqBoxSend(self, ProgressBarUpdate):
        print('Start reqBoxSend().')
        self.upload_progress = 0 # 清空上傳進度

        if not self.connection : raise SystemError('Server not connection.')
        if not self.packaged : raise SystemError('File does not yet have packingBox()')


        header = {
            'file_name': self.file_name,  # file name
            'file_size': self.file_size,  # bytes
            'tar_size': self.tar_size,    # tar_size != file_size
            'file_type': self.file_type   # .txt
        }

        status = { 'code' : 110 , 'header': header}
        package = json.dumps(status).encode('UTF-8')

        try: # send Box header
            self.client.settimeout(5)
            self.client.sendall(package)
        except:
            print('--Fail to reqBoxSend() send header')
            return False

        print('reqBoxSend() send header succeed.')

        # Start send Box
        sent_size = 0
        file_location = f'{self.cache_tar_upload}/{self.file_name}.tar'
        with open(file_location, 'rb') as f :
            while True:
                try:
                    bytes_read = f.read(self.chunk_size)  # read file

                    if not bytes_read:
                        print('reqBoxSend() All send successfully.')
                        break

                    self.client.sendall(bytes_read)

                    sent_size += self.chunk_size
                    self.upload_progress = countProgress(sent_size, self.file_size) # 計算上傳進度
                    ProgressBarUpdate.emit() # PYQT5 --------------------------------------------------
                except Exception as e:
                    print('--reqBoxSend() Failed to send Box.')
                    print(e)
                    f.close()
                    os.remove(file_location) # remove upload cache
                    self.packaged = False
                    self.upload_progress = 0
                    self.stop()
                    return False

            f.close()
            self.upload_progress = 100
            ProgressBarUpdate.emit() # PYQT5 --------

        self.packaged = False
        f.close()
        os.remove(file_location) # remove upload cache

        try: # Receive receive Box key
            received_package = self.client.recv(self.chunk_size)
        except:
            print('--reqBoxSend() Failed to receive Box key.')
            self.stop()
            return False

        self.client.settimeout(None)
        status = json.loads(received_package.decode('UTF-8'))
        # print('reqBoxSend() recv status = ', status)

        if status['code'] == 114: # 寄件失敗
            return False

        return status['data']['key'] # 寄件成功 回傳取件碼






    def reqBoxHeader(self, boxKey):
        print('Start reqBoxHeader().')
        if not self.connection : raise SystemError('Server not connection.')

        data = {'key' : boxKey}
        status = { 'code' : 120 , 'data' : data}
        package = json.dumps(status).encode('UTF-8')

        try: # Ask if the Box exists
            self.client.settimeout(5)
            self.client.sendall(package)
        except:
            print('--reqConnection() Failed to send package')
            self.stop()
            self.connection = False
            return False

        try: # Receive Box header
            received_package = self.client.recv(self.chunk_size)
        except:
            print('--reqConnection() Failed to receive Box header.')
            self.stop()
            self.connection = False
            return False

        self.client.settimeout(None)
        status = json.loads(received_package.decode('UTF-8'))
        print('recv status = ', status)

        if status['code'] == 123:
            print('--reqBoxHeader() Box not found.')
            return False

        print('reqBoxHeader() Box found.')
        header = status['header']
        self.box_name = header['file_name']
        self.box_type = header['file_type']
        self.box_file_size = header['file_size'] 
        self.box_size = header['tar_size'] # tar_size
        return True


    def reqBoxRecv(self, boxKey, ProgressBarUpdate=None):
        print('Start reqBoxRecv().')
        if not self.connection : raise SystemError('Server not connection.')
        if not self.save_folder : raise SystemError('save_folder not set.')
        if not self.box_name or not self.box_size or not self.box_file_size : 
            raise SystemError('Have not Box info, run reqBoxHeader() first.')

        data = {'key' : boxKey}
        status = { 'code' : 122 , 'data' : data}
        package = json.dumps(status).encode('UTF-8')

        try: # Ask if the Box exists
            self.client.settimeout(5)
            self.client.sendall(package)
        except:
            print('--reqBoxRecv() Failed to send package.')
            self.stop()
            self.connection = False
            return False

        # start recv tar Box
        file_location = f'{self.cache_tar_download}/{boxKey}.tar'
        # print('reqBoxRecv() file_location: ',file_location)

        SUCCESS_WRITE = self.writeData(file_location, ProgressBarUpdate)
        self.client.settimeout(None)
        
        if SUCCESS_WRITE == False :
            print('--reqBoxRecv() Failed to recv Box, remove cache')
            os.remove(file_location)
            return False
        
        print('reqBoxRecv() Box recv successfully, file_location = ', file_location)

        save_name = f'received_{getTime()}_{self.box_name}' # 解 tar 後儲存的名稱
        SUCCESS_TAR_OPEN = self.unpackBox(boxKey, save_name)

        if SUCCESS_TAR_OPEN == False :
            print('--reqBoxRecv.unpackBox() unpack failed.')
            return False

        print('reqBoxRecv.unpackBox() succeed.')
        return True


    def writeData(self, file_location, ProgressBarUpdate): ### Don't call this
        error_bytes = json.dumps({ 'code' : 124 }).encode('UTF-8')
        self.download_progress = 0

        try:
            with open(file_location, 'wb') as f:

                received_size = 0
                while not received_size == self.box_size:
                    try:
                        bytes_read = self.client.recv(self.chunk_size) # read data from server

                        if bytes_read == error_bytes:
                            print('--reqBoxRecv.writeData() boxKey wrong.')
                            return False

                        f.write(bytes_read)

                        received_size += len(bytes_read)
                        self.download_progress = countProgress(received_size, self.box_size)
                        ### ProgressBarUpdate.emit() # PYQT5 --------------------------------------------------
                    except Exception as error:
                        print('--Fail to receive file. it is Server error, check the server sendBox()')
                        print(error)
                        return False

                print('All file received.')
                f.close()
        except:
            print('--reqBoxRecv.writeData() Failed to write data.')
            return False
        return True


    def unpackBox(self, boxKey, save_name): ### Don't call this
        return openTar(boxKey, self.save_folder, save_name, self.cache_tar_download)




    def stop(self):
        print('***Close connection***')
        self.connection = False
        try:
            self.client.settimeout(None)
            self.client.close()
        except:
            print('Not connected to server.')
        return True





    def showConnection(self):
        return self.connection

    def showUploadProgress(self):
        return self.upload_progress

    def showDownloadProgress(self):
        return self.download_progress






# tar_name : 要與生成 tar 的檔案或資料夾的名稱相同
# file_location : 要生成 tar 的檔案或資料夾位置
# cache_tar_folder : 暫存生成的 tar 檔的資料夾位置 (self 有預設路徑)
def generateTar(tar_name, file_location, cache_tar_folder):
    if checkDirExists(cache_tar_folder) == False : raise SystemError('--generateTar() cannot create cache_tar_folder =', cache_tar_folder)

    try:
        tar = tarfile.open(f'{cache_tar_folder}/{tar_name}.tar', 'w')
        tar.add(file_location)
        tar.close()
    except:
        print('--generateTar() Failed to found file_location = ', file_location)
        tar.close()
        os.remove(f'{cache_tar_folder}/{tar_name}.tar') # 打包失敗 清除殘留檔
        return False
    return True



# boxKey : 用拿到的 key 來解tar
# save_folder : 存解 tar 後的檔案位置
# cache_tar_folder : 緩存下載 tar 位置 (self 有預設路徑)
def openTar(boxKey, save_folder, save_name, cache_tar_folder):
    if checkDirExists(save_folder) == False : raise SystemError('--openTar() cannot create save_folder =', save_folder)

    try:
        tar = tarfile.open(f'{cache_tar_folder}/{boxKey}.tar', 'r')
        tar.extractall(f'{save_folder}/{save_name}', numeric_owner = True)
        tar.close()
    except:
        print('--openTar() Fail to found tar file.')
        return False

    try: # 清除緩存 tar 
        os.remove(f'{cache_tar_folder}/{boxKey}.tar')
    except:
        print('--openTar() Failed to remove download cache.')

    return True











def countProgress(a, b):
    percentage = 100 * float(a) / float(b)
    return int(percentage)

def getTime():
    localtime = time.localtime()
    result = time.strftime('%I-%M-%S', localtime)
    return str(result)


def isDir(location):
    return os.path.isdir(location)

def isFile(location):
    return os.path.isfile(location)




def checkDirExists(folder):
    if not isDir(folder) :
        try:
            os.makedirs(folder)
            print('folder not exist, create new one.')
        except:
            print('--folder not exist, failed to create new one.')
            return False
    return True


def get_folder_size(folder):
    total_size = 0
    for root, dirs, files in os.walk(folder):
        for file in files:
            file_path = os.path.join(root, file)
            total_size += os.path.getsize(file_path)
    return total_size






"""
if __name__ == '__main__':
    server_host = '127.0.0.1'#'proxy.ggwp.tw'#'192.168.31.146'#
    server_port = 7000
    file = './test.mp4' # './test_dir'#'./test.txt' #


    client = Client()
    client.setHost(server_host, server_port)
    client.setFile(file)
    client.start()

    print('reqConnection()')
    client.reqConnection()
    time.sleep(1)


    
    print('------------------')
    print('reqBoxSend()')
    #client.packingBox()
    recvKey = client.reqBoxSend()
    print('reqBoxSend() -> recvKey :', recvKey)
    time.sleep(1)


    #boxKey = 'puUU2'#'eSF6t'
    print('------------------')
    print('reqBoxHeader()')
    client.reqBoxHeader(boxKey)
    time.sleep(1)
    print('reqBoxRecv()')
    client.reqBoxRecv(boxKey)

    client.stop()
"""