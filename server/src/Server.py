# -*- coding: utf-8 -*-

import socket, pickle, os, threading, random#, #pymongo


"""
# Status Code

Client 100 : 檢查連接
Server 200: 連接成功(server res) 

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




class Server():
    def __init__(self):
        self.host = '0.0.0.0'
        self.port = 7000
        self.dataBase = None
        self.depot = './depot'

        self.MONGO_URL = None
        self.DATABASE_NAME = None
        self.DATABASE_COLLECTION = None

        self.KEY_LENGTH = 5

        self.max_listening = 10  # max waiting count
        self.chunk_size = 1024
        self.users = {}




    ### Initialization settings -----------------------------------------------------------------------------------------------------------

    def setHost(self, host, port):
        self.host = host
        self.port = int(port)
        return True

    def setDepot(self, depot):
        self.depot = depot
        return True

    def setDataBase(self, DB_url, DB_name, DB_col):
        self.MONGO_URL = DB_url
        self.DATABASE_NAME = DB_name
        self.DATABASE_COLLECTION = DB_col
        return True

    def setKeyLength(self, key_length):
        self.KEY_LENGTH = int(key_length)
        return True

    def setMaxListening(self, max_val):
        self.max_listening = int(max_val)
        return True


    def init(self):
        self.server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.server.bind((self.host, self.port))
        self.dataBase = dataBase(self.MONGO_URL, self.DATABASE_NAME, self.DATABASE_COLLECTION) # connect MongoDB

        print('Host: ', self.host)
        print('Port: ', self.port)
        print('Deport: ', self.depot)
        print('DB_url: ', self.MONGO_URL)
        print('DB_name: ', self.DATABASE_NAME)
        print('DB_col: ', self.DATABASE_COLLECTION)
        print('key_len: ', self.KEY_LENGTH)
        print('max_listening: ', self.max_listening)

        if not os.path.isdir(self.depot) :
            try:
                os.makedirs(self.depot)
                print('depot folder not exist, create new one.')
            except:
                print('--depot folder not exist, failed to create new one.')
                return False

        print('Successfully Initialized Server.')
        return True


    ### Server start -----------------------------------------------------------------------------------------------------------

    def startListening(self):
        self.server.listen(self.max_listening)
        print(f'Server start listening {self.server.getsockname()[0]}:{self.server.getsockname()[1]}...')
        while True:

            ### connection count test
            # main = threading.Thread(target=self.mainThread, args=(), daemon=True)
            # main.start()
            # print('main.start()')

            try:
                client, client_address = self.server.accept()
                self.users[client_address] = client
                print(f'Client connect successful {self.users[client_address].getpeername()[0]}:{self.users[client_address].getpeername()[1]}')

                thread = threading.Thread(target=self.recvStatus, args=(self.users[client_address], client_address), daemon=True)
                thread.start()
            except:
                print('***Stop listening***')
                return False


    #def mainThread(self): ### connection count test
    #    while True:
    #        print('users: ',len(self.users))
    #        time.sleep(1)


    def recvStatus(self, client, client_address):
        while True:
            try:
                client.settimeout(5)
                package = client.recv(self.chunk_size)
                status = pickle.loads(package)
                print(f'status = {str(status)}')
            except:
                print(f"Close connect client {client_address}")
                client.settimeout(None)
                client.close()
                self.users.pop(client_address)
                return False


            # sort by status code
            code = status['code']

            if code == 100:
                self.sendConnection(client) # -> (200)
            elif code == 110:
                self.recvBox(client, status['header']) # -> (111) (114)
            elif code == 120:
                self.searchBox(client, status['data']) # -> (121) (123)
            elif code == 122:
                self.sendBox(client, status['data']) # -> (124) (125)


    ### Execute methods -----------------------------------------------------------------------------------------------------------

    def sendConnection(self, client):
        status = { 'code' : 200 }
        package = pickle.dumps(status)

        try:
            client.sendall(package)
        except:
            print('--sendConnection() Failed to response status = ', status)
            return False

        print('sendConnection() succeed.')
        return True


    def recvBox(self, client, header):
        boxKey = generateKey(self.KEY_LENGTH)

        while True:
            query = {'key' : boxKey}
            if DB_find(self.dataBase, query) != False:
                boxKey = generateKey(self.KEY_LENGTH)
            else:
                break


        newBox = {
            'key' : boxKey,
            'file_name': header['file_name'],
            'file_type': header['file_type'],
            'file_size': header['file_size'],
            'tar_size': header['tar_size']
        }
        print('recvBox() newBox = ', newBox)


        # 設置暫存包裹位置 './depot/[boxKey].tar'
        # 以 tar 暫存所有包裹
        file_location = f'{self.depot}/{boxKey}.tar'
        SUCCESS_WRITE = writeData(client, self.chunk_size, file_location, header['tar_size'])


        if SUCCESS_WRITE == False : # 沒成功寫入 刪除暫存
            print('--recvBox() Failed to recv Box, remove cache.')
            os.remove(file_location)
        else :
            self.dataBase.insert_one(newBox) # 成功寫入才插入 dataBase

        # 111: 寄件成功
        # 114: 寄件失敗
        code = 111 if (SUCCESS_WRITE != False) else 114

        status = { 'code' : 114 }
        if code == 111 :
            data = {'key': boxKey}
            status = { 'code' : 111 , 'data': data}

        package = pickle.dumps(status)

        try:
            client.sendall(package)
        except:
            print('--recvBox() Failed to send boxKey to client ', status)
            return False

        print('recvBox() succeed.')
        #client.close()
        return True


    def searchBox(self, client, data):
        status = { 'code' : 123 }

        try:
            boxKey = data['key']
            query = {'key' : boxKey}
            resultData = DB_find(self.dataBase, query)
            print('searchBox() resultData = ', resultData)

            if resultData != False :
                header = {
                    'file_name': resultData['file_name'],
                    'file_type': resultData['file_type'],
                    'file_size': resultData['file_size'],
                    'tar_size': resultData['tar_size']
                }
                status = { 'code' : 121 , 'header' : header}
        except:
            print('--searchBox.DB_find() Failed to find data.')
            status = { 'code' : 123 }


        print('searchBox() = ', status)
        package = pickle.dumps(status)

        try:
            client.sendall(package)
        except:
            print('--searchBox() Failed to res header.')
            return False

        print('searchBox() succeed.')
        return True


    def sendBox(self, client, data):
        status = { 'code' : 124 }

        try:
            boxKey = data['key']
            query = {'key' : boxKey}
            resultData = DB_find(self.dataBase, query)
            print('sendBox() resultData = ', resultData)

            if resultData != False :
                file_location = f'{self.depot}/{boxKey}.tar'
                print('sendBox() file_location: ', file_location)

                readData(client, self.chunk_size, file_location)
            
            else :
                print('sendBox() boxKey not found.')
                package = pickle.dumps(status)

                try:
                    client.sendall(package)
                except:
                    print('--sendBox() boxKey not found, then return(124) errors.')
                    return False
        except:
            print('--sendBox.DB_find() dataBase errors.')
            package = pickle.dumps(status)

            try:
                client.sendall(package)
            except:
                print('--sendBox() Fail to response error (124) client errors.')
                return False

        print('sendBox() succeed.')
        return True




### Private methods -----------------------------------------------------------------------------------------------------------

def writeData(client, chunk_size, file_location, file_size):
    
    try:
        with open(file_location, 'wb') as f:

            received_size = 0
            while not received_size == file_size:
                try:
                    bytes_read = client.recv(chunk_size) # recv data from Client
                except:
                    print('--writeData() Failed to receive file.')
                    return False

                f.write(bytes_read)
                received_size += len(bytes_read)

            print('writeData() All file received.')
            f.close()
    except Exception as error:
        print('--writeData() Failed to write data')
        print(error)
        return False
    return True


def readData(client, chunk_size, file_location):
    try:
        with open(file_location, 'rb') as f :
            while True:
                bytes_read = f.read(chunk_size)  # read file

                if not bytes_read:
                    print('readData() All send successfully.')
                    break

                try:
                    client.sendall(bytes_read)
                except:
                    print('--readData() Client disconnect.')
                    return False

            f.close()
    except Exception as error:
        print('--readData() Failed to read data')
        print(error)
        return False
    return True


def dataBase(DB_url, DB_name, DB_col):

    mongo = pymongo.MongoClient(DB_url)

    DB_list = mongo.list_database_names()
    if not DB_name in DB_list:
        print('DataBase not exists, create new one')

    dataBase = mongo[DB_name]
    collection = dataBase[DB_col]
    return collection


def DB_find(db, query):
    resData = db.find_one(query)

    if resData == None:
        return False
    else:
        return resData


def generateKey(length):
    availableChars = 'ABCDEFGHIJKLMNOPQRSTUVWXYZabcdefghijklmnopqrstuvwxyz0123456789'

    boxKey = ''
    for _ in range(length):
        boxKey += availableChars[random.randint(0, len(availableChars) - 1)]
    return boxKey



"""
if __name__ == '__main__':
    server_host = '0.0.0.0' #os.getenv('SERVER_HOST')#'0.0.0.0'#'192.168.31.146'#'127.0.0.1'#
    server_port = 8000 #os.getenv('SERVER_PORT')#
    server_depot = './asd' #os.getenv('DEPOT') #'./depot'

    DB_url = 'mongodb://localhost:27017'
    DB_name = 'test'
    DB_col = 'lst'

    print('Host: ', server_host)
    print('Port: ', server_port)
    print('Deport: ', server_depot)


    #
    server = Server()
    server.setHost(server_host, server_port)
    server.setDepot(server_depot)
    server.setDataBase(DB_url, DB_name, DB_col)
    server.init()
    server.startListening()
    #server.stop()
    #
"""