[`Client`](#client) 模塊文檔


## Client

### 初始化設定
```py
Client()
```

<details> <summary>Example Code</summary>

```py
from src.tcp.Client import Client
client = Client() 
```

</details>
<br>




### 參數設定
#### 設定Host
```py
setHost(host: str, port: int) -> bool
```
必要參數  
`host`: 目標 Server 的 ip 或 domain name    
`port`: 目標 Server 所使用的 port (Server 預設值 7000)  


#### 設定檔案來源
```py
setFile(file_location: str) -> bool
```
必要參數  
`file_location`: 選擇要上傳的檔案或資料夾的**相對路徑**或**絕對路徑**  

<details> <summary>Example Code</summary>

```py
from src.tcp.Client import Client
client = Client()
client.setHost('192.168.1.20', 7000)
client.setFile('./homework') # 要上傳的檔案或資料夾的相對路徑
# or
client.setFile('C:/Users/usr/Desktop/folder/test.mp4') # 要上傳的檔案或資料夾的絕對路徑
# or
client.setFile('C:\\Users\\usr\\Desktop\\folder\\test.mp4') # 輸入雙反斜線`setFile()`會自動修改
```

</details>
<br>


#### 設定下載資料夾
預設值為 `./save`  
```py
setSaveFolder(save_folder: str) -> bool
```
必要參數  
`save_folder`: 儲存已下載檔案的所在資料夾的相對路徑或絕對路徑，如果該位置未存在資料夾則自動生成    

<details> <summary>Example Code</summary>

```py
from src.tcp.Client import Client
client = Client()
client.setHost('192.168.1.20', 7000)
client.setSaveFolder('./save') # Client 端儲存檔案所使用的資料夾的相對路徑
# or
client.setSaveFolder('C:/Users/usr/Desktop/save') # Client 端儲存檔案所使用的資料夾的絕對路徑
# or
client.setSaveFolder('C:\\Users\\usr\\Desktop\\save') # 輸入雙反斜線`setSaveFolder()`會自動修改
```

</details>
<br>




### Client 啟動
#### 須先[設定參數](#參數設定)才能啟動
開始請求與伺服器連接，回傳布林值
```py
start() -> bool
```

<details> <summary>Example Code</summary>

```py
from src.tcp.client import Client
client = Client()
client.setHost('192.168.1.20', 5000)
client.setFolder('./folder/test.mp4')
client.start()
"""
輸出:
Start connecting 192.168.1.20:7000

連接成功輸出:
Connect to server successfully 192.168.1.20:7000

連接失敗輸出:
--Fail to connect, try again.
--Fail to connect, try again.
--Fail to connect, try again.
--Unable to connect to Server.
"""
```

</details>
<br>




### 請求連接狀態
請求與伺服器當前的連接狀態，回傳布林值
```py
reqConnection() -> bool
```

<details> <summary>Example Code</summary>

```py
from src.tcp.client import Client
client = Client()
client.setHost('192.168.1.20', 5000)
client.setFolder('./folder/test.mp4')
client.start()

client.reqConnection()
"""
輸出:
Start checking connection status.

連接正常輸出:
Server connection status (200) ok.

連接不正常輸出:
--Fail to receive Server connection Status.

請求失敗輸出:
--reqConnection() Fail to send package to Server.
"""
```

</details>
<br>




### 打包檔案
#### 須先[設定檔案來源](#設定檔案來源)才能調用該函數
把要上傳的檔案打包成 tar 檔(包裹)  
並暫存在 `cache_tar_upload` 的位置等待上傳包裹  
```py
packingBox() -> bool
```

<details> <summary>Example Code</summary>

```py
...

client.packingBox()
"""
輸出:
Start packingBox().

打包成功輸出:
packingBox() succeed.

打包失敗輸出:
--packingBox() Failed.
"""
```

</details>
<br>




### 請求上傳包裹
#### 須先[打包檔案](#打包檔案)才能調用該函數
向 Server 發送包裹(tar 檔)  
發送成功回傳 `取件碼(boxKey)` ，失敗則回傳 `False`  
```py
reqBoxSend() -> boxKey | False
```

<details> <summary>Example Code</summary>

```py
...

client.reqBoxSend()
"""
輸出:
Start reqBoxSend().

發送成功輸出:
reqBoxSend() All send successfully.

發送失敗輸出:
--reqBoxSend() Failed to send Box.

接收取件碼失敗輸出:
--reqBoxSend() Failed to receive Box key.
"""
```

</details>
<br>




### 請求包裹標頭
用取件碼向 Server 請求對應的包裹標頭  
```py
reqBoxHeader(boxKey: str) -> bool
```
`True` : 找到包裹  
`False` : 未找到包裹，包裹不存在  

<details> <summary>Example Code</summary>

```py
...

client.reqBoxHeader()
"""
輸出:
Start reqBoxHeader().

找到包裹輸出:
reqBoxHeader() Box found.

查無包裹輸出:
--reqBoxHeader() Box not found.
"""
```

</details>
<br>




### 請求接收包裹
#### 須先[請求包裹標頭](#請求包裹標頭)才能調用該函數
因為需要先儲存 `reqBoxHeader()` 取得的包裹標頭  
用取件碼向 Server 請求對應的包裹  
返回的包裹是 tar 檔的形式  
會暫存在 `cache_tar_download` 的位置解開包裹後存入指定的下載資料夾  
```py
reqBoxRecv(boxKey: str) -> bool
```
`True` : 包裹接收成功，並成功解開儲存  
`False` : 未找到包裹，包裹不存在，或解包失敗(無權限才會解包失敗)  

<details> <summary>Example Code</summary>

```py
...

client.reqBoxRecv()
"""
輸出:
Start reqBoxRecv().

接收包裹成功輸出:
reqBoxRecv() Box recv successfully, file_location = ./cache_tar_download/boxKey.tar

接收包裹失敗輸出:
--reqBoxRecv() Failed to recv Box, remove cache

解開包裹成功輸出:
reqBoxRecv.unpackBox() succeed.

解開包裹失敗輸出:
--reqBoxRecv.unpackBox() unpack failed.
"""
```

</details>
<br>




### 關閉連接
#### [`Client.start()`](#client-啟動) 後才能調用
```py
stop() -> bool
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
<br>




### 其他函式
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
<br>


#### 顯示發送包裹進度
```py
showUploadProgress() -> int
```
回傳值為整數`int` 0-100

<details> <summary>Example Code</summary>

```py
...
print(f'Uploading: {client.showUploadProgress()} %')
client.reqBoxSend()
print(f'Uploading: {client.showUploadProgress()} %')
"""
輸出:
Uploading: 0 %

開始發送包裹輸出:
Start reqBoxSend().

成功發送包裹完成輸出:
reqBoxSend() All send successfully.

Uploading: 100 %
"""
```

</details>
<br>


#### 顯示接收包裹進度
```py
showDownloadProgress() -> int
```
回傳值為整數`int` 0-100

<details> <summary>Example Code</summary>

```py
...
print(f'Downloading: {client.showDownloadProgress()} %')
client.reqBoxRecv()
print(f'Downloading: {client.showDownloadProgress()} %')
"""
輸出:
Downloading: 0 %

開始接收包裹輸出:
Start reqBoxRecv().

成功接收包裹完成輸出:
reqBoxRecv() Box recv successfully, file_location = ./cache_tar_download/boxKey.tar

Downloading: 100 %
"""
```

</details>
<br>
