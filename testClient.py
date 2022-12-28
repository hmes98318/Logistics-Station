from src.tcp.Client import *


if __name__ == '__main__':
    server_host = '127.0.0.1'#'192.168.31.146'#
    server_port = 7000
    file = './docs/client.md' #'./test.mp4' # './test_dir'#'./test.txt' #


    client = Client()
    client.setHost(server_host, server_port)
    client.setFile(file)
    client.start()

    print('reqConnection()')
    client.reqConnection()
    time.sleep(1)


    """
    print('------------------')
    print('reqBoxSend()')
    client.packingBox()
    recvKey = client.reqBoxSend()
    print('reqBoxSend() -> recvKey :', recvKey)
    time.sleep(1)
    """

    boxKey = 'BjHRY'#'eSF6t'
    """
    print('------------------')
    print('reqBoxHeader()')
    client.reqBoxHeader(boxKey)
    time.sleep(1)
    print('reqBoxRecv()')
    client.reqBoxRecv(boxKey)
    """
    client.stop()