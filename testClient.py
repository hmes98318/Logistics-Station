from tcp.Client import Client
import time


if __name__ == '__main__':
    server_host = '127.0.0.1'#'127.0.0.1'#
    server_port = 7777
    save_folder = './save'#'C:/Users/usr/Desktop/p2py/save'#'C:\\Users\\usr\\Desktop\\p2py' #

    client = Client()
    client.setHost(server_host, server_port)
    client.setFolder(save_folder)

    client.start()
    client.askHeader()
    time.sleep(1)
    print(f'connection: {client.showConnection()}')
    time.sleep(1)
    print('download: '+str(client.showProgress()))
    client.askFile()
    print('download: '+str(client.showProgress()))
    client.stop()
    print(f'connection: {client.showConnection()}')