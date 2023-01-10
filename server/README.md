#  Logistics-Station Server Deployment Document


## Deploying with Python

### Preconditions
 * [MongoDB](https://www.mongodb.com/)
 * [Python 3.10](https://www.python.org/downloads/release/python-3109/)


### Start MongoDB
Windows  
```
cd 'C:\Program Files\MongoDB\Server\6.0\bin'
./mongod --dbpath c:\MongoDB\data\db
```

Mac  
```
brew services start mongodb-community@6.0
```
The version number at the end changes according to the installed version.  


### Open Directory
```
cd server/
```


### Install Python modules
[`requirements.txt`](./requirements.txt)
```
pip install -r requirements.txt
```


### Configure Environment
[`.env`](./.env)
```env
SERVER_PORT = 7000  # Listening port
DEPOT = ./depot     # The mount point where the file is temporarily stored

MONGO_URL = mongodb://localhost:27017
DATABASE_NAME = Logistics-Station
DATABASE_COLLECTION = data

KEY_LENGTH = 5      # Generated pickup code length
MAX_LISTENING = 10
```


### Start the Server
```
python ./startServer.py
```




## Deploying with Docker Compose
image link : https://hub.docker.com/r/hmes98318/logistics-station

### Configuration [`docker-compose.yml`](./docker-compose.yml)
```yml
version: '3.8'

services:

  server:
    image: hmes98318/logistics-station:1.1.0
    container_name: logistics-station
    restart: always
    ports:
      - 7000:7000
    environment:
      - SERVER_PORT=7000
      - DEPOT=/data/depot
      - MONGO_URL=mongodb://logistics:dbpAssw0rd@db:27017/
      - DATABASE_NAME=Logistics-Station
      - DATABASE_COLLECTION=data
      - KEY_LENGTH=5
      - MAX_LISTENING=10
    volumes:
      - /usr/local/logistics-station/depot:/data/depot
    depends_on:
      - db
    networks:
      - logistics-net

  db:
    image: mongo
    container_name: logistics-db
    restart: always
    ports:
      - 27017:27017
    environment:
      - MONGO_INITDB_ROOT_USERNAME=logistics
      - MONGO_INITDB_ROOT_PASSWORD=dbpAssw0rd
    volumes:
      - /usr/local/logistics-station/data/db:/data/db
    networks:
      - logistics-net

networks:
  logistics-net:
```


### Start the Container
```
docker-compose up -d
```