導入 [`Server`](#server), [`Client`](#client) 模塊教學


## Server

### 導入模塊
```py
from src.tcp.server import Server
```


### 初始化模塊
```py
Server([max_listening: int])
```
可選參數  
`max_listening`: 最大等待連接數  

<details> <summary>Example Code</summary>

```py
from src.tcp.server import Server

server = Server() # `max_listening`使用預設值 1
# or
server = Server(10) # max_listening = 10
```

</details>


### Server 參數設定
#### 設定Host
```py
setHost([host: str, port: int])
```
可選參數  
`host`: Server 的 ip 位置，預設值 `0.0.0.0`  
`port`: Server 所使用的 port，預設值 `7777`  

#### 設定檔案來源
```py
setFile(file_location: str)
```
必要參數  
`file_location`: Server 端所要分享的檔案的相對路徑或絕對路徑  

<details> <summary>Example Code</summary>

```py
from src.tcp.server import Server

server = Server()
server.setHost('192.168.1.20', 5000) # 如果未調用該函式則使用預設值 ('0.0.0.0', 7777)

server.setFile('./folder/test.py') # 使用相對路徑導入 test.py
# or
server.setFile('C:/Users/usr/Desktop/ftpy/folder/test.py') # 使用絕對路徑導入 test.py
```

</details>


### Server 初始化
#### 須先[設定 Server 參數](#server-參數設定)才能初始化
```py
init()
```

<details> <summary>Example Code</summary>

```py
from src.tcp.server import Server

server = Server()
server.setHost('192.168.1.20', 5000)
server.setFile('./folder/test.py')
server.init()

"""
初始化成功輸出:
---Successfully Initialized Server---
"""
```

</details>


### Server 開始聆聽請求
#### 等待 Client 發出 [`askHeader()`](#請求檔案-header) 或 [`askFile()`](#請求檔案內容)
```py
startListening()
```
請求內容  
`askHeader()`: 送出檔案名稱, 大小  
`askFile()`: 送出檔案內容，完成後自動關閉連接  

<details> <summary>Example Code</summary>

```py
from src.tcp.server import Server

server = Server()
server.setHost('192.168.1.20', 5000)
server.setFile('./folder/test.py')
server.init()
server.startListening()

"""
輸出:
server start listening 192.168.1.20:5000...

連接成功輸出:
Client connect successful 192.168.2.12:60943

askHeader() 請求返回成功輸出:
Send header successfully

askFile() 請求返回成功輸出:
--All send successfully
Close connect client ('192.168.2.12', 60943)
"""
```

</details>


### Server 關閉連接
#### [`Server.init()`](#server-初始化) 後才能成功調用
```py
stop()
```

<details> <summary>Example Code</summary>

```py
...

server.stop()

"""
關閉連接輸出:
***Close server***
"""
```

</details>


### Server 其他函式
#### 顯示已連接使用者
```py
showUser()
```
<details> <summary>Example Code</summary>

```py
...

print(server.showUser())

"""
輸出:
{
    ('192.168.2.12', 61640): <socket.socket fd=4, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('192.168.1.20', 5000), raddr=('192.168.2.12', 61640)>,
    ('192.168.2.34', 53526): <socket.socket fd=4, family=AddressFamily.AF_INET, type=SocketKind.SOCK_STREAM, proto=0, laddr=('192.168.1.20', 5000), raddr=('192.168.2.34', 53526)>
}
"""
```

```py
...

print(f'users: {len(server.showUser())}') # 顯示當前連接人數

"""
輸出:
users: 2
"""
```

</details>



## Client

### 導入模塊
```py
from src.tcp.client import Client
```


### 初始化模塊
```py
Client()
```

<details> <summary>Example Code</summary>

```py
from src.tcp.client import Client

client = Client() 
```

</details>


### Client 參數設定
#### 設定Host
```py
setHost(host: str, port: int)
```
必要參數  
`host`: 目標 Server 的 ip 位置  
`port`: 目標 Server 所使用的 port  

#### 設定檔案儲存資料夾
```py
setFolder(save_folder: str)
```
必要參數  
`save_folder`: Client 端儲存檔案的所在資料夾的相對路徑或絕對路徑    

<details> <summary>Example Code</summary>

```py
from src.tcp.client import Client

client = Client()
client.setHost('192.168.1.20', 5000)

client.setFolder('./save') # Client 端儲存檔案所使用的資料夾的相對路徑
# or
client.setFolder('C:/Users/usr/Desktop/ftpy/save') # Client 端儲存檔案所使用的資料夾的絕對路徑
```

</details>


### Client 啟動
#### 須先[設定 Client 參數](#client-參數設定)才能啟動
```py
start()
```

<details> <summary>Example Code</summary>

```py
from src.tcp.client import Client

client = Client()
client.setHost('192.168.1.20', 5000)
client.setFolder('./save')
client.start()

"""
輸出:
start connecting 192.168.1.20:5000

啟動成功輸出:
Connect to server successfully 192.168.1.20:5000
"""
```

</details>


### 請求檔案 Header
#### [`Client.start()`](#client-啟動)後才能成功調用
```py
askHeader()
```

<details> <summary>Example Code</summary>

```py
from src.tcp.client import Client

client = Client()
client.setHost('192.168.1.20', 5000)
client.setFolder('./save')
client.start()
client.askHeader()

"""
Header 輸出:
{
    'file_name': 'test.py',
    'file_size': 4345
}
"""
```

</details>


### 請求檔案內容
#### [`Client.start()`](#client-啟動)後才能成功調用，須先 [`askHeader()`](#請求檔案-header) 獲取目標檔案 header，完成後會自動關閉連接
```py
askFile()
```

<details> <summary>Example Code</summary>

```py
from src.tcp.client import Client

client = Client()
client.setHost('192.168.1.20', 5000)
client.setFolder('./save')
client.start()
client.askHeader()
client.askFile()
"""
檔案內容接收成功輸出:
--All file received
"""
```

</details>


### Client 關閉連接
#### [`Client.start()`](#client-啟動) 後才能成功調用
```py
stop()
```

<details> <summary>Example Code</summary>

```py
...

client.stop()

"""
關閉連接輸出:
***Close connection***
"""
```

</details>


### Client 其他函式
#### 顯示連接狀態
```py
showConnection()
```

<details> <summary>Example Code</summary>

```py
...

print(f'Connection: {client.showConnection()}')
client.stop()
print(f'Connection: {client.showConnection()}')

"""
輸出:
connection: True
***Close connection***
connection: False
"""
```

</details>
