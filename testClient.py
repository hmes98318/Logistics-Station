from src.client import Client


if __name__ == '__main__':
    server_host = '192.168.31.146'#'127.0.0.1'#
    server_port = 7777
    save_folder = './save'

    client = Client(server_host, server_port, save_folder)
    client.start()
    client.getHeader()
    client.getFile()
    client.stop()