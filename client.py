# -*- coding: utf-8 -*-


import socket
import tqdm
import os
import time
import pickle


def client(save_folder):

    host = '127.0.0.1'#'192.168.31.146'#
    port = 7777
    Buffer_size = 4096

    SEPARATOR = '<SEPARATOR>'

    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    print(f'start connecting {host}:{port}')
    client.connect((host, port))
    print('connection success')

    received = client.recv(Buffer_size)#.decode("UTF-8")
    unserial_file = pickle.loads(received)
    filename ,file_size = unserial_file.split(SEPARATOR)
    print(f'fetch file: {filename} ,size: {file_size}')


    dirCheck(save_folder) # Check if the folder exist

    with open(f'{save_folder}received_{getTime()}_'+filename,'wb') as f:
        progress = tqdm.tqdm(range(int(file_size)), f'receive {filename}', unit='K', unit_divisor=1024, unit_scale=True)

        
        for _ in progress:
            bytes_read = client.recv(Buffer_size) # 從 server 讀取數據

            if not bytes_read: # 如果沒有數據傳入
                break

            f.write(bytes_read) # 讀取寫入
            #print(bytes_read)
            progress.update(len(bytes_read)) # 更新進度條
        
        



    # close connection
    client.close()



def getTime():
    localtime = time.localtime()
    result = time.strftime("%I-%M-%S", localtime)
    return str(result)


def dirCheck(path):
    if not os.path.isdir(path):
        os.mkdir(path)


if __name__ == '__main__':
    client('./save/')