#  Logistics-Station 的伺服器配置


## 使用 Python 部屬

### 環境配置
 * [MongoDB](https://www.mongodb.com/)
 * [Python 3.10](https://www.python.org/downloads/release/python-3109/)


### 啟動MongoDB
Windows  
```
cd 'C:\Program Files\MongoDB\Server\6.0\bin'
./mongod --dbpath c:\MongoDB\data\db
```

Mac  
```
brew services start mongodb-community@6.0
```
結尾的版本號碼依照安裝的版本更改


### 安裝Python模塊
```
pip install pymongo python-dotenv
```


### 啟動伺服器
```
python ./main.py
```




## 使用 Docker Compose 部屬

image link : https://hub.docker.com/r/hmes98318/logistics-station

### 配置 [`docker-compose.yml`](./docker-compose.yml)
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


### 啟動容器
```
docker-compose up -d
```