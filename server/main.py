# -*- coding: utf-8 -*-

import os
from src.Server import *

from dotenv import load_dotenv
load_dotenv()


if __name__ == '__main__':
    server_host = os.getenv('SERVER_HOST') if (os.getenv('SERVER_HOST') != None ) else '0.0.0.0'
    server_port = os.getenv('SERVER_PORT') if (os.getenv('SERVER_PORT') != None ) else 7000
    server_depot = os.getenv('DEPOT') if (os.getenv('DEPOT') != None ) else './depot'


    DB_url = os.getenv('MONGO_URL') if (os.getenv('MONGO_URL') != None ) else 'mongodb://localhost:27017'
    DB_name = os.getenv('DATABASE_NAME') if (os.getenv('DATABASE_NAME') != None ) else 'Logistics-Station'
    DB_col = os.getenv('DATABASE_COLLECTION') if (os.getenv('DATABASE_COLLECTION') != None ) else 'data'

    key_len = os.getenv('KEY_LENGTH') if (os.getenv('KEY_LENGTH') != None ) else 5
    max_listening = os.getenv('MAX_LISTENING') if (os.getenv('MAX_LISTENING') != None ) else 5


    server = Server()

    server.setHost(server_host, int(server_port))
    server.setDepot(server_depot)
    server.setDataBase(DB_url, DB_name, DB_col)
    server.setKeyLength(key_len)
    server.setMaxListening(max_listening)
    server.init()

    server.startListening()
    # server.stop()