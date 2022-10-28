from src.server import Server
import time


if __name__ == '__main__':
    server_host = '192.168.31.146'#'0.0.0.0'#'127.0.0.1'#
    server_port = 7777
    server_filename = 'test.7z'
    server_filelocation = './tmp/test.7z'

    server = Server(server_host, server_port, server_filename, server_filelocation)
    
    while True:
        server.start()
        time.sleep(8)
        server.status()
        server.sendHeader()
        server.sendFile()
        server.stop()