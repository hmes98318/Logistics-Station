from tcp.Server import Server
import time


if __name__ == '__main__':
    server_host = '0.0.0.0'#'0.0.0.0'#'127.0.0.1'#
    server_port = 7777
    server_filelocation = './tmp/01.py'

    
    server = Server()
    server.setHost(server_host, server_port)
    server.setFile(server_filelocation)
    server.init()
    server.startListening()
    #server.stop()