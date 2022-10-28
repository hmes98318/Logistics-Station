# -*- coding: utf-8 -*-


import socket
from tqdm import tqdm
import os
import re
import pickle


def server(file_addr):

    sever_host = '192.168.31.146'#sever_host = '127.0.0.1'
    sever_port = 7777
    server_listening = 128
    Buffer_size = 4096

    

    while True:
        server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        server.bind((sever_host, sever_port))
        server.listen(server_listening)
        print(f'server start listening {sever_host}:{sever_port}')


        while True:
            file_name = getFileName(file_addr)

            # shareFile(file_addr, file_name, server, Buffer_size)

            SEPARATOR = '<SEPARATOR>'
            file_size  = os.path.getsize(file_addr)

            client_socket, client_address = server.accept()
            print(f'client {client_address} connection success')

            serial_file = pickle.dumps(f'{file_name}{SEPARATOR}{file_size}')
            #client_socket.sendall(f'{file_name}{SEPARATOR}{file_size}'.encode("UTF-8"))
            client_socket.sendall(serial_file)
            print(f'{file_name}{SEPARATOR}{file_size}')


            with open(file_addr,'rb') as f :
                progress = tqdm(range(file_size), f'send{file_name}', unit='K', unit_divisor=1024)
                # read file
                for _ in progress:
                    bytes_read = f.read(Buffer_size)
                    if not bytes_read:
                        print("\nsuccess send!")
                        break

                    try:
                        client_socket.sendall(bytes_read)
                        progress.update(len(bytes_read))
                    except :
                        print("\nclient close connection")
                        break
                
            # close connection
            client_socket.close()
            print("connection close")
            break

        server.close()


"""
def shareFile(file_addr, file_name, server, Buffer_size):
    SEPARATOR = '<SEPARATOR>'
    file_size  = os.path.getsize(file_addr)

    client_socket, client_address = server.accept()
    print(f'client {client_address} connection success')

    serial_file = pickle.dumps(f'{file_name}{SEPARATOR}{file_size}')
    #client_socket.sendall(f'{file_name}{SEPARATOR}{file_size}'.encode("UTF-8"))
    client_socket.sendall(serial_file)
    print(f'{file_name}{SEPARATOR}{file_size}')

    progress = tqdm.tqdm(range(file_size), f'send{file_name}', unit='B', unit_divisor=1024)

    with open(file_addr,'rb') as f :
        # read file
        for _ in progress:
            bytes_read = f.read(Buffer_size)
            if not bytes_read:
                break

            client_socket.sendall(bytes_read)
            progress.update(len(bytes_read))

    # close connection
    client_socket.close()
    print("connection close")

"""

def getFileName(file_addr):
    split_file = re.split('\/',file_addr)
    return split_file[len(split_file)-1]







if __name__ == '__main__':
    server('./tmp/Triangle.java')