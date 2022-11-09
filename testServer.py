from src.server import Server
import time


if __name__ == '__main__':
    server_host = '192.168.31.146'#'0.0.0.0'#'127.0.0.1'#
    server_port = 7777
    server_filelocation = './tmp/01.txt'

    
    server = Server()
    server.setHost(server_host, server_port)
    server.setFile(server_filelocation)
    server.init()
    server.startListening()
    #server.stop()